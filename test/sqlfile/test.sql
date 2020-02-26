use test;
create table `student`(
`id_t1` bigint auto_increment primary key comment '主键',
`name` varchar(20) not null comment '姓名',
`age` int,
`grade` int,
`birth_day` datetime not null comment '出生日期',
'date_update' datetime not null comment '记录更新时间',
unique (name))
engine=innodb comment '学生表'
;

delimiter //
CREATE DEFINER=`root`@`%` PROCEDURE `test`.`TEST_PROC`(IN in_param1 int,OUT out_param2 varchar(30), INOUT out_param3 int)
begin
select 3 into out_param3 from dual;
set  out_param2 = 'out_param2';
select id,name from t3  limit 1;
select * from t3 limit 1;
end//

delimiter $$
create definer=`root`@`%` trigger test.trigger_student after update on student for each row
begin
update student a set a.date_update = sysdate() where a.id_t1 = new.id_t1;
end$$

delimiter ;
insert into student(name,age,grade,birth_day)values('张三','20',18,'2020/02/20 15:00:00');
commit;

alter table test.student add c1 varchar(10);