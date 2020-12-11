from enum import Enum

from deploy.transform import oper, ds

from deploy.transform.oracle2mysql import stage

SQL_LIST = {
    #为了重复执行，需要删掉由之前运行的，可能存在的临时表
    stage.PREPARE:(
        (oper.EXEC,ds.ORACLE,'''drop table vcms_city_area_tab''',0),
        (oper.EXEC,ds.ORACLE,'''drop table vcms_upgrd_devc_map_tab''',0),
        (oper.EXEC,ds.ORACLE,'''drop table T_CITYCODE''',0),
        (oper.EXEC,ds.ORACLE,'''drop table t_cfg_dict''',0),
        (oper.EXEC,ds.ORACLE,'''drop table vcms_upgrd_office_map_tab''',0),
        (oper.EXEC,ds.ORACLE,'''drop table vcms_upgrd_usrgrp_map_tab''',0)
    ),
    #创建临时表，准备迁移过程中的转换规则
    stage.CREATE_UPD_TABLES:(
        (oper.EXEC,ds.ORACLE,'''create table vcms_city_area_tab(area_code varchar2(20),  area_name varchar2(600),  province_id varchar2(2),   city_id varchar2(2))'''),
        (oper.EXEC,ds.ORACLE,'''create table vcms_upgrd_devc_map_tab(old_device_id varchar2(50) not null,new_device_id varchar2(50) not null)'''),
        (oper.EXEC,ds.ORACLE,'''create unique index idx_vcms_upgrd_devc_map_tab_od on vcms_upgrd_devc_map_tab(old_device_id)'''),
        (oper.EXEC,ds.ORACLE,'''create unique index idx_vcms_upgrd_devc_map_tab_nd on vcms_upgrd_devc_map_tab(new_device_id)'''),
        (oper.EXEC,ds.ORACLE,'''create table vcms_upgrd_office_map_tab(old_office_id number,new_office_id varchar2(20))'''),
        (oper.EXEC,ds.ORACLE,'''create unique index idx_vcms_upgrd_office_map_oid on vcms_upgrd_office_map_tab(old_office_id)'''),
        (oper.EXEC,ds.ORACLE,'''create unique index idx_vcms_upgrd_office_map_nid on vcms_upgrd_office_map_tab(new_office_id)'''),
        (oper.EXEC,ds.ORACLE,'''CREATE TABLE t_citycode(area_code varchar2(60) NOT NULL,area_name varchar2(600) NOT NULL)'''),
        (oper.EXEC,ds.ORACLE,'''CREATE TABLE t_cfg_dict(dict_id integer NOT NULL, dict_code varchar2(150) NOT NULL, col_name varchar2(150), dict_note varchar2(900), up_dict integer)'''),
        (oper.EXEC,ds.ORACLE,'''create table vcms_upgrd_usrgrp_map_tab(old_group_id varchar2(50),new_group_id varchar2(50))'''),
        (oper.EXEC,ds.ORACLE,'''create unique index idx_vcms_upgrd_usrgrp_map_ogd on vcms_upgrd_usrgrp_map_tab(old_group_id)'''),
        (oper.EXEC,ds.ORACLE,'''create unique index idx_vcms_upgrd_usrgrp_map_ngd on vcms_upgrd_usrgrp_map_tab(new_group_id)'''),
    ),
    #从mysql迁移一部分字典数据到ORACLE，因为两边有一些字典定义冲突，需要做对应的转换
    stage.INIT_DATA:(
        (oper.INSERT,ds.MYSQL,'''select area_code,area_name from usmsc.t_citycode''',ds.ORACLE,'''insert into t_citycode(area_code,area_name) values(:1,:2)'''),
        (oper.INSERT,ds.MYSQL,'''select dict_id ,dict_code,col_name,dict_note,up_dict from t_cfg_dict''',ds.ORACLE,'''insert into t_cfg_dict(dict_id ,dict_code,col_name,dict_note,up_dict)values(:1,:2,:3,:4,:5)''')
    ),
    #初始的校验，可能校验上面两步的结果是否达到期望
    stage.PREPARE_VERIFY:(

    ),
    #开始真正的生成转换规则数据，以及转换后的数据从oracle迁移到mysql对应的表
    stage.MAKE_UPD_DATA:(
        (oper.EXEC,ds.ORACLE,'''insert into vcms_city_area_tab 
select a.area_code||'00',a.area_name,b.province_id,b.city_id 
from  (select n1.area_code,n1.area_name,n2.area_name province_name 
              from  T_CITYCODE n1,T_CITYCODE n2 where n2.area_code like '%0000' and substr(n2.area_code,1,2) = substr(n1.area_code,1,2))a,
      city b,province p where a.area_name=b.city_name and b.province_id = p.province_id and p.province_name = a.province_name'''),
        (oper.EXEC,ds.ORACLE,"""declare
c_di  constant varchar2(7)  := '00134';
c_di_cut constant number  := -6;
c_di_length constant number  := 7;

c_dc  constant varchar2(7)  := '00114';
c_dc_cut constant number  := -6;
c_dc_length constant number  := 7;

c_cmr  constant varchar2(7)  := '00131';
c_cmr_cut constant number  := -6;
c_cmr_length constant number  := 7;

c_ec constant varchar2(7) := '00111';
c_ec_cut constant number  := -6;
c_ec_length constant number  := 7;

c_pf_cut constant number  := -3;
c_pf_length constant number  := 4;

c_vw constant varchar2(7) := '00177';
c_vw_cut constant number  := -6;
c_vw_length constant number  := 7;

c_zero constant char(1) := '0';
v_mas_seq number;
begin
  
insert into vcms_upgrd_office_map_tab(old_office_id,new_office_id)
select a.office_id,b.area_code||'2'||lpad(a.office_id,4,'0')
from office a,vcms_city_area_tab b
where a.province_id=b.province_id
and   a.city_id=b.city_id;

  /*
alarm_di设备转换设备ID规则，原设备规则为”省编码(15)+市编码(01)+01+123+扩充为6位长度的seq“，
转换为规则”新的区域编码+00+00+134+扩充为7位的seq“
encoder_deviceid来自于encoder的 device_id字段，按照encoder的转换规则转换即可 
*/
/*
DECODER转换规则，decoder_id原始规则：“两位省编码+两位市编码+01+114+扩充为6位长度的seq”
新规则：“新的区域码+00+114+扩充为7为的seq”
connect_server_id按照platform_device的主键变化即可
*/

/*
t_objects与电视墙相关，按照电视墙的规则转换
原始规则：“两位省编码+两位市编码+01+177+扩充为6为的seq”
新规则：“区域码+00+00+177+扩展为7位的seq”
*/
  insert into vcms_upgrd_devc_map_tab(new_device_id,old_device_id)
  select b.area_code||c_di||lpad(to_number(substr(a.device_id,c_di_cut)),c_di_length,c_zero),a.device_id 
  from  alarm_di a, vcms_city_area_tab b 
  where a.device_id like b.province_id||b.city_id||'%'
  union all
  select b1.area_code||c_dc||lpad(to_number(substr(a1.decoder_id,c_dc_cut)),c_dc_length,c_zero),a1.decoder_id 
  from  decoder a1, vcms_city_area_tab b1
  where a1.decoder_id like b1.province_id||b1.city_id||'%'
  union all
  select b2.area_code||c_vw||lpad(to_number(substr(a2.device_id,c_vw_cut)),c_vw_length,'0'),a2.device_id 
  from  t_objects a2, vcms_city_area_tab b2 
  where a2.device_id like b2.province_id||b2.city_id||'%'; 


   
  /*
CAMERA设备ID转换规则，原设备存在两种规则，1：“两位省编码+两位市编码+01+121+扩充为6位长度的seq“
2：“cmcc标志为1的device，规则为connect_device前11位+01+扩充为2位的connect_port”
转换为规则“新的区域码+00+131+扩充为7位的seq”
其中，connect_device与control_device值相同，来自于encoder的 device_id字段，按照encoder的转换规则转换即可
*/
  select max(to_number(substr(a.camera_id,c_cmr_cut))) into v_mas_seq from camera a where a.camera_id <> substr(a.connect_device,1,11)||'01'||lpad(a.connect_port,2,'0'); 
  insert into vcms_upgrd_devc_map_tab(new_device_id,old_device_id)
  select d1.area_code||c_cmr||case a1.camera_id 
           when substr(a1.connect_device, 1, 11) || '01' || lpad(a1.connect_port, 2, '0') then lpad(v_mas_seq+a1.rn,c_dc_length,'0')
           else lpad(substr(a1.camera_id,c_cmr_cut),c_dc_length,'0') end,a1.camera_id
  from (select a.*,
               row_number() over(partition by(
               case when a.camera_id <>  substr(a.connect_device,1,11) || '01' || lpad(a.connect_port, 2, '0') 
                   then 1 else 0 end) order by rownum) rn  from camera a) a1,device b1,office c1,vcms_city_area_tab d1
  where a1.camera_id = b1.device_id
  and b1.office_id=c1.office_id
  and c1.province_id=d1.province_id
  and c1.city_id=d1.city_id; 
  
  /*
ENCODER编码器ID转换规则，原设备存在两种规则，1：”两位省编码+两位市编码+01+111+扩充为6位长度的seq“
2：“cmcc标志位为1的device，规则为010+0+扩充为7位的seq+00+00“
转换为规则“新的区域码+00+111+扩充为7为的seq”
其中，dispatch_server_id和connect_server_id根据platform_device的主键变化即可
*/
  select max(to_number(substr(a.device_id,c_ec_cut))) into v_mas_seq from ENCODER a where a.device_id not like '0100%0000' ;
  insert into vcms_upgrd_devc_map_tab(new_device_id,old_device_id)
  select d1.area_code||c_ec||case when a1.device_id  like '0100%0000' then lpad(v_mas_seq+a1.rn,c_ec_length,'0')
           else lpad(substr(a1.device_id,c_ec_cut),c_ec_length,'0') end,a1.device_id
  from (select a.*,
               row_number() over(partition by(
               case when a.device_id not like '0100%0000' 
                   then 1 else 0 end) order by rownum) rn  from ENCODER a) a1,device b1,office c1,vcms_city_area_tab d1
  where a1.device_id = b1.device_id
  and b1.office_id=c1.office_id
  and c1.province_id=d1.province_id
  and c1.city_id=d1.city_id; 
  
  /*
PLATFORM_DEVICE转换规则，有三种规则，1：“固定150101”
2：“两位省编码+两位市编码+01+23+扩充为3为的seq”
3：cmcc为1的,“010+0+扩充为7位的seq+99+00”
center_server_id与主键规则一致
新规则：area_code+扩充为2位的device_kind+扩充为4位的seq
*/

  select max(to_number(substr(a.platform_device_id,c_pf_cut))) into v_mas_seq from PLATFORM_DEVICE a where a.platform_device_id not like '0100%9900' and a.platform_device_id <> '150101';
  insert into vcms_upgrd_devc_map_tab(new_device_id,old_device_id)
  select d1.area_code||lpad(b1.device_kind,2,'0')||case when a1.platform_device_id  like '0100%9900' then lpad(v_mas_seq+a1.rn,c_pf_length,'0') when a1.platform_device_id='150101' then '01'
             else lpad(substr(a1.platform_device_id,c_pf_cut),c_pf_length,'0') end,a1.platform_device_id
    from (select a.*,
                 row_number() over(partition by(
                 case when a.platform_device_id not like '0100%9900' 
                     then 1 when a.platform_device_id='150101' then 2  else 0 end) order by rownum) rn  from PLATFORM_DEVICE a) a1,device b1,office c1,vcms_city_area_tab d1
  where a1.platform_device_id = b1.device_id
  and b1.office_id=c1.office_id
  and c1.province_id=d1.province_id
  and c1.city_id=d1.city_id; 
  
/*
设备组的组id转换规则，设备组的id一部分来自于平台设备，这部分id在上面已经做过转换，不用处理；另一部分是N+1的组id，需要转换一下。
规则为
N+1组，两位省编码+两位市编码+01+9+扩充为5位长度的seq。N+1不存在device表中
最后一种，cmcc:"010"+"01"+"9"+扩充为5位的seq
转换为规则“新的区域码+00+(201|202)+扩充为7位的序列号”.
*/
insert into vcms_upgrd_devc_map_tab(new_device_id,old_device_id)
select (
       select n2.area_code from vcms_city_area_tab n2 where (n2.province_id,n2.city_id)=
        (select n1.province_id,n1.city_id from office n1 where n1.office_id=1 and a.group_id like '010019%' 
        union all
        select substr(a.group_id,1,2),substr(a.group_id,3,2) from dual where  a.group_id not like '010019%' 
        )    
)||'201'||lpad(substr(a.group_id,-5),7,'0'),
       a.group_id
from t_device_group a where not exists (select 1 from device d1 where d1.device_id = a.group_id );

/*
用户组的组id转换规则：
    旧规则：非cmcc：
                两位省编码(00)+两位市编码(00)+018+扩充为5位的seq
            cmcc：
                "010"+"01"+"8"+扩充为5位的seq
    
    new：区域码+12+扩充为5位的序列
*/  

insert into vcms_upgrd_usrgrp_map_tab(old_group_id,new_group_id)
select a.user_group_id,
(select n2.area_code from vcms_city_area_tab n2 where (n2.province_id,n2.city_id)=
        (select n1.province_id,n1.city_id from office n1 where n1.office_id=1 and (a.user_group_id like '0000%' or a.user_group_id like   '010018%')
        union all
        select substr(a.user_group_id,1,2),substr(a.user_group_id,3,2) from dual where  a.user_group_id not like '0000%' and a.user_group_id not like '010018%'
        )
)||'12'||substr(a.user_group_id,-5)
from t_user_group a;

end;"""),
        (oper.EXEC,ds.MYSQL,'''SET GLOBAL foreign_key_checks = 0''',0),
        (oper.EXEC,ds.MYSQL,'''SET foreign_key_checks = 0''',0),
        (oper.EXEC,ds.MYSQL,'''drop trigger tr_int_precinct''',0),
        (oper.EXEC,ds.MYSQL,'''drop trigger tr_del_precinct''',0),
        (oper.EXEC,ds.MYSQL,'''drop trigger tr_int_device''',0),
        (oper.EXEC,ds.MYSQL,'''drop trigger tr_upd_device''',0),
        (oper.EXEC,ds.MYSQL,'''drop trigger tr_del_device''',0),
        #迁移区域表
        (oper.INSERT,ds.ORACLE,'''select b.area_code||'2'||lpad(a.office_id,4,'0') precinct_id ,2 lsc_id,a.office_name precinct_name,
(case when a.upoffice_id='0' then '010100000' else (select b1.area_code||'2'||lpad(a1.office_id,4,'0') from office a1,vcms_city_area_tab b1  where a1.office_id=a.upoffice_id and a1.province_id=b1.province_id and  a1.city_id=b1.city_id) end) up_precinct_id
,0 precinct_kind,null domain_id,b.area_code area_code
from office a,vcms_city_area_tab b
where a.province_id=b.province_id
and   a.city_id=b.city_id''',ds.MYSQL,'''insert into t_cfg_precinct(precinct_id,lsc_id,precinct_name,up_precinct_id,precinct_kind,domain_id,area_code) values(%s,%s,%s,%s,%s,%s,%s)'''),
        #迁移设备表
        (oper.INSERT,ds.ORACLE,'''with odata as (
select ltrim(rtrim(connect_by_root(o1.parameter_note))) root_note,ltrim(rtrim(o1.parameter_note)) current_note,
sys_connect_by_path(o1.parameter_note,',') path,
o1.parameter_code,o1.parameter_value 
from SYSTEM_PARAMETER o1 start with o1.parameter_value='device_kind' and o1.up_parameter='0' 
connect by prior o1.parameter_type=o1.up_parameter),
tdata as (select ltrim(rtrim(connect_by_root(t1.dict_note))) root_note,ltrim(rtrim(t1.dict_note)) current_note,
sys_connect_by_path(t1.dict_note,',') path,t1.dict_code,t1.col_name 
from  t_cfg_dict t1
connect by prior t1.dict_id=t1.up_dict
start with t1.col_name='device_kind' and t1.up_dict=0)
select b.new_device_id device_id ,c.new_office_id precinct_id,null station_id,a.device_name device_name,
nvl((select a1.dict_code from  tdata a1,odata b1 where b1.parameter_value ='device_kind' and a1.col_name = 'device_kind' and b1.parameter_code=a.device_kind and b1.current_note=a1.current_note and b1.root_note=a1.root_note and rownum =1),a.device_kind ) device_kind,
case when a.device_type='0' then  decode(nvl(a.device_kind,0),'4','120100','3','12544','100100') else  nvl((select a1.dict_code 
  from  tdata a1,odata b1       
  where b1.parameter_value ='device_type' and a1.col_name = 'device_type' 
      and b1.parameter_code=a.device_type 
      and a1.path=b1.path and rownum=1),a.device_type ) end device_type,
a.manufacture_id manufacture_id,null model_id,a.use_time launchtime,null user_device_id,a.device_seq device_index,a.device_use_state device_use_state,a.device_model device_model,a.purchase_time purchase_time,
a.use_time use_time,a.use_years use_years,a.update_time update_time,a.install_site install_site,a.device_principal device_principal,a.principal_tel principal_tel,a.principal_email principal_email,null pre_del,a.x,a.y
from  device a,vcms_upgrd_devc_map_tab b,vcms_upgrd_office_map_tab c
where a.device_id=b.old_device_id
and   a.office_id=c.old_office_id''',ds.MYSQL,'''insert into t_cfg_device(device_id,  precinct_id,  station_id,  device_name,  device_kind,  device_type,  manufacture_id,  model_id,  launchtime,  user_device_id,  device_index,  device_use_state,  device_model,  purchase_time,  use_time,  use_years,  update_time,  install_site,  device_principal,  principal_tel,  principal_email,  pre_del,  X,  Y)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''),
        #迁移alarm_di
        (oper.INSERT,ds.ORACLE,'''select b.new_device_id device_id,c.new_device_id encoder_deviceid,a.di_port di_port,a.alarm_type alarm_type,a.alarm_level alarm_level,a.di_state di_state,a.description description
from  ALARM_DI a,vcms_upgrd_devc_map_tab b,vcms_upgrd_devc_map_tab c where a.device_id=b.old_device_id and a.encoder_deviceid=c.old_device_id''',ds.MYSQL,'''insert into t_video_alarmdi(device_id,encoder_deviceid,di_port,alarm_type,alarm_level,di_state,description)values(%s,%s,%s,%s,%s,%s,%s)'''),
        #迁移摄像头
        (oper.INSERT,ds.ORACLE,'''select b.new_device_id camera_id,
(select a1.new_device_id from  vcms_upgrd_devc_map_tab a1 where a1.old_device_id=a.connect_device ) connect_device,
a.connect_port connect_port,a.ptz_protocol ptz_protocol,
(select a1.new_device_id from  vcms_upgrd_devc_map_tab a1 where a1.old_device_id=a.control_device ) control_device,
a.control_port control_port,a.port_param port_param,a.address address,a.is_controlable is_controlable,a.pos_control pos_control,
a.control_type control_type,a.bitrate bitrate,a.resolution resolution,a.encodemode encodemode,null ia_server_id,null diag_state,null direction_type,null position_type,a.ptz_type ptz_type,null room_type,null supplylight_type,null use_type,null ip_address,null listen_port,null user_name,null user_pwd,null camera_model,null nvr_device_id,null nvr_port,null publish_status
from  camera a,vcms_upgrd_devc_map_tab b,device c where a.camera_id=b.old_device_id and a.camera_id=c.device_id''',ds.MYSQL,'''insert into t_video_camera(camera_id,connect_device,connect_port,ptz_protocol,control_device,control_port,port_param,address,is_controlable,pos_control,control_type,bitrate,resolution,encodemode,ia_server_id,diag_state,direction_type,position_type,ptz_type,room_type,supplylight_type,use_type,ip_address,listen_port,user_name,user_pwd,camera_model,nvr_device_id,nvr_port,publish_status)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''),
        #迁移编码器
        (oper.INSERT,ds.ORACLE,'''select b.new_device_id device_id,a.ip_address ip_address,a.listen_port listen_port,a.inport_num inport_num,
a.outport_num outport_num,a.pswd pswd,a.device_user_name device_user_name,a.multicast_addr multicast_addr,
(select a1.new_device_id from  vcms_upgrd_devc_map_tab a1 where a1.old_device_id=a.connect_server_id) connect_server_id,
a.di_num di_num,a.do_num do_num,a.web_page web_page,a.mac_addr mac_addr,a.md5_pwd md5_pwd,a.encoder_state encoder_state,
(select a1.new_device_id from  vcms_upgrd_devc_map_tab a1 where a1.old_device_id=a.dispatch_server_id) dispatch_server_id,
a.encoder_type encoder_type,a.subnetmask subnetmask,a.gateway gateway,a.register_time register_time,a.need_alarmreport need_alarmreport,null ipc_fg,null regist_to_csg,null uuid
 from  ENCODER a,vcms_upgrd_devc_map_tab b where a.device_id=b.old_device_id ''',ds.MYSQL,'''insert into t_video_encoder(device_id,ip_address,listen_port,inport_num,outport_num,pswd,device_user_name,multicast_addr,connect_server_id,di_num,do_num,web_page,mac_addr,md5_pwd,encoder_state,dispatch_server_id,encoder_type,subnetmask,gateway,register_time,need_alarmreport,ipc_fg,regist_to_csg,uuid)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''),
        #路由转发
        (oper.INSERT,ds.ORACLE,'''select b.new_device_id device_id,
(select a1.new_device_id from  vcms_upgrd_devc_map_tab a1 where a1.old_device_id=a.dispatch_server_id) dispatch_server_id,
(select a1.new_device_id from  vcms_upgrd_devc_map_tab a1 where a1.old_device_id=a.encoder_id) encoder_id,
a.outport outport,a.link_model link_model,a.multicast_addr multicast_addr,a.dispatch_link_model dispatch_link_model,a.is_server_transmit is_server_transmit,
a.multicast_port multicast_port
from  VIDEO_ROUTER a,vcms_upgrd_devc_map_tab b,camera c where c.camera_id=b.old_device_id and a.encoder_id=c.connect_device and a.outport=c.connect_port''',ds.MYSQL,'''insert into t_video_router(device_id,dispatch_server_id,encoder_id,outport,link_model,multicast_addr,dispatch_link_model,is_server_transmit,multicast_port)values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'''),
        #解码器
        (oper.INSERT,ds.ORACLE,'''select b.new_device_id decoder_id,a.ip_address ip_address,a.listen_port listen_port,a.outport_num outport_num,
a.device_user_name device_user_name,a.pswd pswd,
(select a1.new_device_id from  vcms_upgrd_devc_map_tab a1 where a1.old_device_id=a.connect_server_id) connect_server_id,
a.di_num di_num,a.do_num do_num,a.web_page web_page,a.md5_pwd md5_pwd,a.subnetmask subnetmask,a.gateway gateway,null decoder_state
 from  DECODER a ,vcms_upgrd_devc_map_tab b where a.decoder_id=b.old_device_id''',ds.MYSQL,'''insert into t_video_decoder(decoder_id,ip_address,listen_port,outport_num,device_user_name,pswd,connect_server_id,di_num,do_num,web_page,md5_pwd,subnetmask,gateway,decoder_state)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''),
        #平台设备
        (oper.INSERT,ds.ORACLE,'''select  b.new_device_id device_id,a.service_addr service_addr,a.service_port service_port,
(select a1.new_device_id from  vcms_upgrd_devc_map_tab a1 where a1.old_device_id=a.center_server_id) up_server_id
,a.web_page web_page,
a.login_state login_state,a.sip_port sip_port,a.private_service_addr private_service_addr,a.subnetmask subnetmask,a.gateway gateway,
a.rtsp_port rtsp_port,a.http_port http_port,a.icpusummit iCPUSummit,a.imemsummit iMemSummit,a.isendsummit iSendSummit,a.irecvsummit iRecvSummit,null connect_num,null is_lb,null lb_server_id,null down_server_id
from  PLATFORM_DEVICE a,vcms_upgrd_devc_map_tab b where a.platform_device_id=b.old_device_id''',ds.MYSQL,'''insert into t_cfg_nmsdevice(device_id,service_addr,service_port,up_server_id,web_page,login_state,sip_port,private_service_addr,subnetmask,gateway,rtsp_port,http_port,iCPUSummit,iMemSummit,iSendSummit,iRecvSummit,connect_num,is_lb,lb_server_id,down_server_id)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''),
        #电视墙
        (oper.INSERT,ds.ORACLE,'''select b.new_device_id device_id,a.x1 x1,a.y1 y1,
(select a1.new_device_id from  vcms_upgrd_devc_map_tab a1 where a1.old_device_id=a.decoder_id) decoder_id,
a.x2 x2,a.y2 y2,a.output_num output_num,a.nos nos,a.is_alarmrect is_alarmrect,a.output_num outputindex,null channelindex
from GT_SCREENWALL_RECT a,vcms_upgrd_devc_map_tab b where a.device_id=b.old_device_id''',ds.MYSQL,'''insert into t_video_screenwallrect(device_id,x1,y1,decoder_id,x2,y2,output_num,nos,is_alarmrect,outputindex,channelindex)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''),
        #设备扩展属性
        (oper.INSERT,ds.ORACLE,'''select b.new_device_id device_id,a.extend_pro extend_col,a.extend_pro_value extend_col_value
from  T_DEVICE_EXTEND a,vcms_upgrd_devc_map_tab b where a.device_id=b.old_device_id''',ds.MYSQL,'''insert into t_cfg_deviceextend(device_id,extend_col,extend_col_value)values(%s,%s,%s)'''),
        #对象
        (oper.INSERT,ds.ORACLE,'''select a.objects_id objects_id,b.new_device_id device_id ,a.objects_name objects_name,a.up_objects up_objects,
a.creator_id creator_id,a.create_time create_time,a.objects_type objects_type
from  t_objects a,vcms_upgrd_devc_map_tab b where a.device_id=b.old_device_id''',ds.MYSQL,'''insert into t_cfg_objects(objects_id,device_id,objects_name,up_objects,creator_id,create_time,objects_type)values(%s,%s,%s,%s,%s,%s,%s)'''),
        #区域关系
        (oper.INSERT,ds.ORACLE,'''
with t as (
select b.area_code||'2'||lpad(a.office_id,4,'0') office_id,
(case when a.upoffice_id='0' then '010100000' else (select b1.area_code||'2'||lpad(a1.office_id,4,'0') from office a1,vcms_city_area_tab b1  where a1.office_id=a.upoffice_id and a1.province_id=b1.province_id and  a1.city_id=b1.city_id) end) upoffice_id
from office a,vcms_city_area_tab b
where a.province_id=b.province_id
and   a.city_id=b.city_id
)
select '010100000' precinct_id,'010100000' precinct_down from dual
union all
select '010100000',office_id from t
union all
select connect_by_root(office_id),office_id from t connect by prior office_id = upoffice_id''',ds.MYSQL,'''replace into t_precinct_relation(precinct_id,precinct_down)values(%s,%s)'''),
        #生成不同分类的序列最大值
        (oper.INSERT,ds.ORACLE,'''select 'replace into usmsc.t_cfg_maxobjectid values(' || device_kind || ',' || va || ');'
  from (select device_kind,
               max(case
                     when device_kind in '1' then
                      to_number(substr(b.new_device_id, -4)) + 1
                     when device_kind in ('2', '3', '4', '5', '7') then
                      to_number(substr(b.new_device_id, -7)) + 1
                   end) va
          from device a, vcms_upgrd_devc_map_tab b
         where a.device_id = b.old_device_id(+)
         group by a.device_kind)''',ds.MYSQL,None),
        #存储配置
        (oper.INSERT,ds.ORACLE,'''select b.new_device_id device_id,(select b1.new_device_id from vcms_upgrd_devc_map_tab b1 where b1.old_device_id = a.store_server_id) store_server_id,b.new_device_id encoder_id,a.outport,
a.store_model,a.sunday,a.monday,a.tuesday,a.wednesday,a.thursday,a.friday,a.saturday,a.holiday,a.saveday,a.isspace,a.spacesize,a.record_fg,a.pre_record,a.delay_time
 from  video_store a ,vcms_upgrd_devc_map_tab b where a.encoder_id=b.old_device_id''',ds.MYSQL,'''insert into usmsc.t_video_store (`device_id`,`store_server_id`,`encoder_id`,`outport`,`store_model`,`sunday`,`monday`,`tuesday`,`wednesday`,`thursday`,`friday`,`saturday`,`holiday`,`saveday`,`isspace`,`spacesize`,`record_fg`,`pre_record`,`delay_time`) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''),
        #备份存储设置
        (oper.INSERT,ds.ORACLE,'''select b.new_device_id device_id,(select b1.new_device_id from vcms_upgrd_devc_map_tab b1 where b1.old_device_id = a.store_server_id) store_server_id,b.new_device_id encoder_id,
a.outport,a.bak_type,a.store_model,a.sunday,a.monday,a.tuesday,a.wednesday,a.thursday,a.friday,a.saturday,a.holiday,a.saveday,a.isspace,a.spacesize,a.record_fg,a.pre_record,a.delay_time
 from  video_store_multi a ,vcms_upgrd_devc_map_tab b where a.encoder_id=b.old_device_id''',ds.MYSQL,'''insert into usmsc.t_video_storemulti (`device_id`,`store_server_id`,`encoder_id`,`outport`,`bak_type`,`store_model`,`sunday`,`monday`,`tuesday`,`wednesday`,`thursday`,`friday`,`saturday`,`holiday`,`saveday`,`isspace`,`spacesize`,`record_fg`,`pre_record`,`delay_time`) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''),
        #设备组
        (oper.INSERT,ds.ORACLE,'''select b.new_device_id group_id,a.group_name ,a.creator_id,a.create_time,a.istateflag,c.new_office_id precinct_id,a.group_kind
from t_device_group a,vcms_upgrd_devc_map_tab b,vcms_upgrd_office_map_tab c
where a.group_id = b.old_device_id
and   a.office_id = c.old_office_id(+)''',ds.MYSQL,'''insert into usmsc.t_video_devicegroup (`group_id`,`group_name`,`creator_id`,`create_time`,`iStateFlag`,`precinct_id`,`group_kind`) values (%s,%s,%s,%s,%s,%s,%s)'''),
        #设备组成员
        (oper.INSERT,ds.ORACLE,'''with odata as (
select ltrim(rtrim(connect_by_root(o1.parameter_note))) root_note,ltrim(rtrim(o1.parameter_note)) current_note,
sys_connect_by_path(o1.parameter_note,',') path,
o1.parameter_code,o1.parameter_value 
from SYSTEM_PARAMETER o1 start with o1.parameter_value='device_kind' and o1.up_parameter='0' 
connect by prior o1.parameter_type=o1.up_parameter),
tdata as (select ltrim(rtrim(connect_by_root(t1.dict_note))) root_note,ltrim(rtrim(t1.dict_note)) current_note,
sys_connect_by_path(t1.dict_note,',') path,t1.dict_code,t1.col_name 
from  t_cfg_dict t1
connect by prior t1.dict_id=t1.up_dict
start with t1.col_name='device_kind' and t1.up_dict=0)
select b.new_device_id group_id,c.new_device_id device_id, 
        nvl((select a1.dict_code 
        from  tdata a1,odata b1       
        where b1.parameter_value ='device_type' and a1.col_name = 'device_type' 
        and b1.parameter_code=a.device_type 
        and a1.path=b1.path and rownum=1),a.device_type ) device_type ,
        a.cur_state,
        a.category_id, 
        nvl((select a1.dict_code 
                  from  tdata a1,odata b1       
                  where b1.parameter_value ='device_type' and a1.col_name = 'device_type' 
                   and b1.parameter_code=a.group_device_type 
                   and a1.path=b1.path and rownum=1),a.group_device_type ) group_device_type
from t_device_group_member a,vcms_upgrd_devc_map_tab b,vcms_upgrd_devc_map_tab c
where a.group_id = b.old_device_id
and   a.device_id = c.old_device_id''',ds.MYSQL,'''insert into usmsc.t_video_devicegroupmember (`group_id`,`device_id`,`device_type`,`cur_state`,`category_id`,`group_device_type`) values (%s,%s,%s,%s,%s,%s)'''),
        #大客户映射到部门
#         (oper.INSERT,ds.ORACLE,'''select  to_number(substr(a.enterprise_id,-5)) dept_id,a.enterprise_name dept_name,0 up_dept_id,a.prefix description,0 dept_kind,a.max_user_number dept_user_cnt,0 vehicle_cnt,a.cmcc_fg,
# (select b.new_office_id from vcms_upgrd_office_map_tab b where a.office_id=b.old_office_id)
# from T_ENTERPRISE a
# where a.enterprise_id not in ('000001')
# and   a.istateflag in (1)''',ds.MYSQL,'''insert into usmsc.t_scim_dept (`dept_id`,`dept_name`,`up_dept_id`,`description`,`dept_kind`,`dept_user_cnt`,`vehicle_cnt`,`cmcc_fg`,`precinct_id`) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)'''),
        #用户信息
        (oper.INSERT,ds.ORACLE,'''with tmp_enterprise as (
select t1.user_id,case t1.enterprise_id when '000001' then 1 else to_number(substr(t1.enterprise_id,-5)) end enterprise_id
from t_client_admin t1
union
select t2.user_id,case t2.enterprise_id when '000001' then 1 else to_number(substr(t2.enterprise_id,-5)) end
from t_client_user t2
)
select a.user_id,(select b.new_office_id from vcms_upgrd_office_map_tab b where a.office_id = b.old_office_id) precinct_id,
decode(a.user_type,3,2,4,3,5,3,a.user_type)  role_id,
(select b1.user_group_id from t_client_user b1 where b1.user_id = a.user_id) usergroup_id,
null department_id,a.user_name,
decode(a.user_type,1,3,2,3,5,10,a.user_type) user_type,
a.user_pwd,null employee_id, null true_name,null mobile_telephone,a.email,a.phone telephone,null address,a.user_state,
a.update_time updatetime,null description,case (select user_name from t_user nt where nt.user_id = a.creator_id ) when  'admin' then '11000000000' when 'global_admin' then '12000000000' else a.creator_id end admin_user,
null fax,null sex,a.user_level,decode(a.login_client_type,2,3,a.login_client_type) login_client_type,a.dtpwupdatetime,a.ivalidtime,null user_img,null user_index,
(select tm2.enterprise_id from tmp_enterprise tm2 where tm2.user_id = a.user_id) dept_id,null flowrole_id,null system_flag,null is_show ,
a.create_time,a.authentication_type  
from t_user a where (a.user_name not in ('global_admin','admin') and a.user_id not in ('000000'))''',ds.MYSQL,'''insert into usmsc.t_cfg_user (`user_id`,`precinct_id`,`role_id`,`usergroup_id`,`department_id`,`user_name`,`user_type`,`user_pwd`,`employee_id`,`true_name`,`mobile_telephone`,`e_mail`,`telephone`,`address`,`user_state`,`updatetime`,`description`,`admin_user`,`fax`,`user_sex`,`user_level`,`login_client_type`,`dtPwUpdateTime`,`iValidTime`,`user_img`,`user_index`,`dept_id`,`flowrole_id`,`system_flag`,`is_show`,`create_time`,`authentication_type`) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''),
        #大客户设备权限  映射为  scim部门设备权限
#         (oper.INSERT,ds.ORACLE,'''select case a.enterprise_id when '000001' then 1 else to_number(substr(a.enterprise_id,-5)) end dept_id,b.new_device_id device_id,null device_kind
# from t_enterprise_device  a,vcms_upgrd_devc_map_tab b
# where a.device_id = b.old_device_id''',ds.MYSQL,'''insert into usmsc.t_scim_dept_device (`dept_id`,`device_id`,`device_kind`) values (%s,%s,%s)'''),
#         #这里要将device_kind从t_cfg_device表更新回来
#         (oper.EXEC,ds.MYSQL,'''update usmsc.t_scim_dept_device a,t_cfg_device b set a.device_kind=b.device_kind where a.device_id=b.device_id'''),
        (oper.INSERT,ds.ORACLE,'''select a1.device_id,case (select user_name from t_user nt where nt.user_id = t1.user_id ) 
when  'admin' then '11000000000' when 'global_admin' then '12000000000' else t1.user_id end user_id,
 '1111111' privilege_flag, b1.device_name,null  device_kind,null device_type, nvl(c1.new_office_id,'010100000') precinct_id,null station_id
from (select n1.user_id,n1.enterprise_id from t_client_admin n1 union select n2.user_id,n2.enterprise_id from  t_client_user n2) t1,
    t_enterprise_device a1,device b1 ,vcms_upgrd_office_map_tab c1
where t1.enterprise_id = a1.enterprise_id
and   a1.device_id = b1.device_id
and   c1.old_office_id(+) = b1.office_id''',ds.MYSQL,'''insert into usmsc.t_cfg_userdevice (`device_id`,`user_id`,`privilege_flag`,`device_name`,`device_kind`,`device_type`,`precinct_id`,`station_id`) values (%s,%s,%s,%s,%s,%s,%s,%s)'''),
        #用户组
        (oper.INSERT,ds.ORACLE,'''with tmp_enterprise as (
select t1.user_id,case t1.enterprise_id when '000001' then 1 else to_number(substr(t1.enterprise_id,-5)) end enterprise_id
from t_client_admin t1
union
select t2.user_id,case t2.enterprise_id when '000001' then 1 else to_number(substr(t2.enterprise_id,-5)) end
from t_client_user t2
)
select c.new_group_id usergroup_id,
(select v1.new_office_id from vcms_upgrd_office_map_tab v1 where v1.old_office_id=nvl(b.office_id,1)) precinct_id,
a.user_group_name usergroup_name,null usergroup_desc,
case (select user_name from t_user nt where nt.user_id = a.creator_id ) when  'admin' then '11000000000' when 'global_admin' then '12000000000' else a.creator_id end creator_id,
nvl((select tm1.enterprise_id from tmp_enterprise tm1 where tm1.user_id = a.creator_id),1) dept_id, 1 is_show
from t_user_group a ,vcms_upgrd_usrgrp_map_tab c,t_user b
where a.creator_id = b.user_id(+)
and  a.istateflag = 1
and  a.user_group_id = c.old_group_id''',ds.MYSQL,'''insert into usmsc.t_cfg_usergroup (`usergroup_id`,`precinct_id`,`usergroup_name`,`usergroup_desc`,`creator_id`,`dept_id`,`is_show`) values (%s,%s,%s,%s,%s,%s,%s)'''),
        #用户组设备权限
        (oper.INSERT,ds.ORACLE,'''select b.new_group_id usergroup_id,(select n1.new_device_id  from vcms_upgrd_devc_map_tab n1 where n1.old_device_id = a.device_id) object_id,
1 object_flag,a.privilege_flag privilege_flag,1 select_flag
from t_group_device a,vcms_upgrd_usrgrp_map_tab b
where a.user_group_id = b.old_group_id''',ds.MYSQL,'''insert into usmsc.t_cfg_usergroupobject (`usergroup_id`,`object_id`,`object_flag`,`privilege_flag`,`select_flag`) values (%s,%s,%s,%s,%s)'''),
        #用户设备权限
        #因为一个设备可以对应多个大客户，但是一个设备仅可以对应一个部门，因此，大客户不再映射到部门，取消大客户的概念。将“设备-大客户-用户”的三层结构修改为“设备-用户”两层结构。
        #这里在原有的数据基础上增加大客户设备到用户的映射
        (oper.INSERT,ds.ORACLE,'''select b.new_device_id device_id,
case (select user_name from t_user nt where nt.user_id = a.user_id ) 
when  'admin' then '11000000000' when 'global_admin' then '12000000000' else a.user_id end user_id,
 a.privilege_flag, null device_name,null device_kind,null device_type,
 (select n1.new_office_id  from vcms_upgrd_office_map_tab n1 where n1.old_office_id = a.office_id) precinct_id,null station_id
 from  T_USER_DEVICE a,vcms_upgrd_devc_map_tab b  
 where a.device_id = b.old_device_id''',ds.MYSQL,'''replace into usmsc.t_cfg_userdevice (`device_id`,`user_id`,`privilege_flag`,`device_name`,`device_kind`,`device_type`,`precinct_id`,`station_id`) values (%s,%s,%s,%s,%s,%s,%s,%s)'''),
        (oper.EXEC,ds.MYSQL,'''update usmsc.t_cfg_userdevice a,t_cfg_device b set a.device_kind=b.device_kind,a.device_type=b.device_type,a.device_name=b.device_name where a.device_id=b.device_id'''),
        #配置admin用户的设备权限
        (oper.EXEC,ds.MYSQL,'''replace into usmsc.t_cfg_userdevice select a.device_id,'11000000000','1111111',a.device_name,a.device_kind,a.device_type,a.precinct_id,'' from t_cfg_device a'''),
        (oper.EXEC,ds.MYSQL,'''replace into usmsc.t_cfg_userdevice select a.device_id,'12000000000','1111111',a.device_name,a.device_kind,a.device_type,a.precinct_id,'' from t_cfg_device a''')
    )
}
