# 数据库 auto_form_filling 文档

## 数据库概览

- 数据库名: auto_form_filling
- 总表数: 30
- 表注释覆盖率: 73.3%
- 列注释覆盖率: 81.8%

## 表详细信息

### LY_MX_XS_JBXX

表名: LY_MX_XS_JBXX
字段数量: 28

字段列表:
- name: varchar 可空 - 姓名
- student_id: varchar 可空 - 学号
- gender: varchar 可空 - 性别
- identity_type: varchar 可空 - 身份证件类型
- unified_authentication_code: varchar 可空 - 统一认证码
- birth_date: varchar 可空 - 出生日期
- age: varchar 可空 - 年龄
- nationality: varchar 可空 - 民族
- native_place: varchar 可空 - 籍贯
- grade: varchar 可空 - 年级
- political_outlook: varchar 可空 - 政治面貌
- belief_religious_code: varchar 可空 - 信仰宗教代码
- marital_status: varchar 可空 - 婚姻状况
- health_status: varchar 可空 - 健康状况
- students_origin_place: varchar 可空 - 生源地
- program_name: varchar 可空 - 专业名称
- college_name: varchar 可空 - 学院名称
- training_level: varchar 可空 - 培养层次
- educational_system: varchar 可空 - 学制
- enrollment_methods: varchar 可空 - 入学方式
- enrollment_date: varchar 可空 - 入学年月
- student_status: varchar 可空 - 学籍状态
- isinschool: varchar 可空 - 是否在校
- certified_phone: varchar 可空 - 认证手机号
- average_GPA: varchar 可空 - 平均成绩绩点
- student_type: varchar 可空 - 学生类型
- phone: varchar 可空 - 联系电话
- sort: varchar 可空 - 本科生研究博士生排序


### logging

表名: logging
字段数量: 3

字段列表:
- user: varchar 可空 - 用户信息
- time: varchar 可空 - 时间
- question: varchar 可空 - 问题


### t_aixl_bkscjpmxx

**表说明**: 本科生成绩排名信息

表名: t_aixl_bkscjpmxx
表说明: 本科生成绩排名信息
字段数量: 11

字段列表:
- wybs: varchar 非空 (主键) - 唯一标识
- xnxq: varchar 可空 - 学年学期
- xh: varchar 可空 - 学号
- pjcjjd: varchar 可空 - 平均成绩绩点
- pjcjjdpm: varchar 可空 - 平均成绩绩点排名
- bxkpjcj: varchar 可空 - 必修课平均成绩
- bxkpjcjpm: varchar 可空 - 必修课平均成绩排名
- frxkpjcj: varchar 可空 - 非任选课平均成绩
- frxkpjcjpm: varchar 可空 - 非任选课平均成绩排名
- tstamp: varchar 可空 - 时间戳
- sfrzh: varchar 可空 - 身份认证号


### t_aixl_bkscjxx

**表说明**: 本科生成绩信息

表名: t_aixl_bkscjxx
表说明: 本科生成绩信息
字段数量: 17

字段列表:
- wybs: varchar 非空 (主键) - 唯一标识
- xh: varchar 可空 - 学号
- xnxq: varchar 可空 - 学年学期
- ksrq: varchar 可空 - 考试日期
- kcbm: varchar 可空 - 课程编码
- ksfsm: varchar 可空 - 考试方式码
- ksxzm: varchar 可空 - 考试性质码
- ksxsm: varchar 可空 - 考试形式码
- cj: varchar 可空 - 成绩
- cjlrrgh: varchar 可空 - 成绩录入人工号
- cjlrsj: varchar 可空 - 成绩录入时间
- xf: varchar 可空 - 学分
- jd: varchar 可空 - 绩点
- gxsj: varchar 可空 - 更新时间
- bz: varchar 可空 - 备注
- tstamp: varchar 可空 - 时间戳
- sfrzh: varchar 可空 - 身份认证号


### t_aixl_bksjbxx

**表说明**: 本科生基本信息

表名: t_aixl_bksjbxx
表说明: 本科生基本信息
字段数量: 38

字段列表:
- wybs: varchar 可空 - 唯一标识
- xh: varchar 非空 (主键) - 学号
- xm: varchar 可空 - 姓名
- wwxm: varchar 可空 - 外文姓名
- xmpy: varchar 可空 - 姓名拼音
- xbm: varchar 可空 - 性别码
- xb: varchar 可空 - 性别
- mzm: varchar 可空 - 民族码
- mz: varchar 可空 - 民族
- lydqm: varchar 可空 - 来源地区码
- syd: varchar 可空 - 生源地
- csrq: varchar 可空 - 出生日期
- csdm: varchar 可空 - 出生地码
- jgm: varchar 可空 - 籍贯码
- gjdqm: varchar 可空 - 国籍地区码
- sfzlxm: varchar 可空 - 身份证类型码
- sfzjh: varchar 可空 - 身份证件号
- sfzjyxq: varchar 可空 - 身份证件有效期
- hyzkm: varchar 可空 - 婚姻状况码
- gatqwm: varchar 可空 - 港澳台侨外码
- zzmmm: varchar 可空 - 政治面貌码
- jkzkm: varchar 可空 - 健康状况码
- xyzjm: varchar 可空 - 信仰宗教码
- xxm: varchar 可空 - 血型码
- sfdszn: varchar 可空 - 是否独生子女
- xslym: varchar 可空 - 学生来源码
- hkxzm: varchar 可空 - 户口性质码
- hkszd: varchar 可空 - 户口所在地
- yzbm: varchar 可空 - 邮政编码
- lxdh: varchar 可空 - 联系电话
- dzyx: varchar 可空 - 电子邮箱
- jstyh: varchar 可空 - 即时通讯号
- tstamp: varchar 可空 - 时间戳
- sjzt: varchar 可空 - 数据状态
- sjztxgsj: datetime 可空 - 数据状态修改时间
- txdz: varchar 可空 - 通讯地址
- cym: varchar 可空 - 曾用名
- sfrzh: varchar 可空 - 身份认证号


### t_aixl_bksjshjxx

**表说明**: 本科学生竞赛获奖信息

表名: t_aixl_bksjshjxx
表说明: 本科学生竞赛获奖信息
字段数量: 7

字段列表:
- xslb: varchar 可空 - 学生列表
- ssmc: varchar 可空 - 赛事名称
- ssjb: varchar 可空 - 赛事级别
- ssdj: varchar 可空 - 赛事等级
- rylb: varchar 可空 - 人员类别
- xh: text 可空 - 学号
- xm: text 可空 - 姓名


### t_aixl_bksjxjxx

**表说明**: 奖助学金信息表

表名: t_aixl_bksjxjxx
表说明: 奖助学金信息表
字段数量: 10

字段列表:
- WID: varchar 非空 (主键) - 无说明
- SJLY: varchar 可空 - 无说明
- XH: varchar 可空 - 学号
- XM: varchar 可空 - 姓名
- NJ: varchar 可空 - 年级
- JXMC: varchar 可空 - 奖项名称
- JXSJ: varchar 可空 - 奖项时间
- YWXTGXSJ: datetime 可空 - 业务系统更新时间
- SCSJ: datetime 可空 - 删除时间
- SFQX: varchar 可空 - 是否取消-1是0否


### t_aixl_bksxjydxx

**表说明**: 本科生学籍异动信息

表名: t_aixl_bksxjydxx
表说明: 本科生学籍异动信息
字段数量: 25

字段列表:
- wybs: varchar 非空 (主键) - 唯一标识
- xh: varchar 可空 - 学号
- xm: varchar 可空 - 姓名
- ydlx: varchar 可空 - 异动类型
- xbjbm: varchar 可空 - 现班级编码
- ydrq: varchar 可空 - 异动日期
- xnj: varchar 可空 - 现年级
- xxz: varchar 可空 - 现学制
- xzybm: varchar 可空 - 现专业编码
- ydlbm: varchar 可空 - 异动类别码
- ydyym: varchar 可空 - 异动原因码
- sprq: varchar 可空 - 审批日期
- spwh: varchar 可空 - 审批文号
- ydsm: varchar 可空 - 异动说明
- yyxbm: varchar 可空 - 原院系编码
- yzybm: varchar 可空 - 原专业编码
- ybjbm: varchar 可空 - 原班级编码
- ynj: varchar 可空 - 原年级
- yxz: varchar 可空 - 原学制
- xyxbm: varchar 可空 - 现院系编码
- xzymc: varchar 可空 - 现专业名称
- xnxq: varchar 可空 - 学年学期
- gxsj: varchar 可空 - 更新时间
- tstamp: varchar 可空 - 时间戳
- sfrzh: varchar 可空 - 身份认证号


### t_aixl_bksxycjxx

**表说明**: 本科生学业成绩信息

表名: t_aixl_bksxycjxx
表说明: 本科生学业成绩信息
字段数量: 10

字段列表:
- sfbkdmmc: varchar 可空 - 是否补考
- xh: varchar 可空 - 学号
- xnxq: varchar 可空 - 学年学期
- xycj: varchar 可空 - 学业成绩
- sfbk: varchar 可空 - 是否补考
- xf: varchar 可空 - 学分
- xncj: varchar 可空 - 学年成绩
- gxsj: varchar 可空 - 更新时间
- tstamp: varchar 可空 - 时间戳
- sfrzh: varchar 可空 - 身份认证号


### t_aixl_bzksxjjbxx

**表说明**: 本专科生学籍基本信息

表名: t_aixl_bzksxjjbxx
表说明: 本专科生学籍基本信息
字段数量: 40

字段列表:
- wybs: varchar 可空 - 唯一标识
- xh: varchar 可空 - 学号
- yxbm: varchar 可空 - 院系编码
- yxmc: varchar 可空 - 院系名称
- zybm: varchar 可空 - 专业编码
- zymc: varchar 可空 - 专业名称
- bjbm: varchar 可空 - 班级编码
- rxny: varchar 可空 - 入学年月
- nj: varchar 可空 - 年级
- xz: varchar 可空 - 学制
- xkmlm: varchar 可空 - 学科门类码
- hdxlfsm: varchar 可空 - 获得学历方式码
- pyccm: varchar 可空 - 培养层次码
- pyfsm: varchar 可空 - 培养方式码
- wtpydw: varchar 可空 - 委托培养单位
- jdfsm: varchar 可空 - 就读方式码
- xslbm: varchar 可空 - 学生类别码
- dywyyzm: varchar 可空 - 第一外语语种码
- dywyspm: varchar 可空 - 第一外语水平码
- dewyyzm: varchar 可空 - 第二外语语种码
- dewyspm: varchar 可空 - 第二外语水平码
- yjbyrq: varchar 可空 - 预计毕业日期
- sjbyrq: varchar 可空 - 实际毕业日期
- sfzc: varchar 可空 - 是否在册
- sfzx: varchar 可空 - 是否在校
- sfzj: varchar 可空 - 是否在籍
- xjztm: varchar 可空 - 学籍状态码
- xjzt: varchar 可空 - 学籍状态
- xsdqztm: varchar 可空 - 学生当前状态码
- pjcjjd: varchar 可空 - 平均成绩绩点
- gxrq: varchar 可空 - 更新日期
- xslxm: varchar 可空 - 学位类型码
- xwlx: varchar 可空 - 学位类型
- bkpc: varchar 可空 - 本科批次
- sfzjm: varchar 可空 - 身份证加密
- tstamp: varchar 可空 - 时间戳
- sfrzh: varchar 可空 - 身份认证号
- xm: varchar 可空 - 姓名
- sjzt: varchar 可空 - 数据状态
- sjztxgsj: datetime 可空 - 数据状态修改时间


### t_aixl_bzksxkxx

**表说明**: 本专科生选课数据_AI

表名: t_aixl_bzksxkxx
表说明: 本专科生选课数据_AI
字段数量: 22

字段列表:
- wybs: varchar 可空 - 唯一标识
- xnxq: varchar 可空 - 学年学期
- xh: varchar 可空 - 学号
- kcbm: varchar 可空 - 课程编码
- bjbm: varchar 可空 - 班级编码
- xksj: varchar 可空 - 选课时间
- xklc: varchar 可空 - 选课轮次
- sfzx: varchar 可空 - 是否重修
- sffx: varchar 可空 - 是否辅修
- njyq: varchar 可空 - 年级要求
- yxyq: varchar 可空 - 院系要求
- zyyq: varchar 可空 - 专业要求
- xkzy: varchar 可空 - 选课志愿
- kclbm: varchar 可空 - 课程类别码
- kclb: varchar 可空 - 课程类别
- fxjxb: varchar 可空 - 分项教学班
- gxsj: varchar 可空 - 更新时间
- xkzt: varchar 可空 - 选课状态
- bz: varchar 可空 - 备注
- tstamp: varchar 可空 - 时间戳
- jxbh: varchar 可空 - 教学班号
- sfrzh: varchar 可空 - 身份认证号


### t_aixl_js_gbrm

表名: t_aixl_js_gbrm
字段数量: 40

字段列表:
- wid: varchar 非空 (主键) - 无说明
- clrq: datetime 可空 - 无说明
- czlx: varchar 可空 - 无说明
- sjly: varchar 可空 - 无说明
- by1: varchar 可空 - 无说明
- by2: varchar 可空 - 无说明
- zwmc: varchar 可空 - 无说明
- zwlbdm: varchar 可空 - 无说明
- zwjbdm: varchar 可空 - 无说明
- rzrq: varchar 可空 - 无说明
- rzdwdm: varchar 可空 - 无说明
- rzfsdm: varchar 可空 - 无说明
- rzwh: varchar 可空 - 无说明
- rzqx: varchar 可空 - 无说明
- rzpzdw: varchar 可空 - 无说明
- zghcsdgz: varchar 可空 - 无说明
- dqrzzkdm: varchar 可空 - 无说明
- sfzz: varchar 可空 - 无说明
- mzrq: varchar 可空 - 无说明
- mzfsdm: varchar 可空 - 无说明
- mzyydm: varchar 可空 - 无说明
- mzwh: varchar 可空 - 无说明
- tjzwrzsj: varchar 可空 - 无说明
- rzjdqk: varchar 可空 - 无说明
- xzzw: varchar 可空 - 无说明
- sfzxsyq: varchar 可空 - 无说明
- syqqssj: varchar 可空 - 无说明
- syqzzsj: varchar 可空 - 无说明
- zzwh: varchar 可空 - 无说明
- zwbdlb: varchar 可空 - 无说明
- jzyy: varchar 可空 - 无说明
- gbjsgljb: varchar 可空 - 无说明
- xjzzwmc: varchar 可空 - 无说明
- rxznx: varchar 可空 - 无说明
- rxzjnx: varchar 可空 - 无说明
- zzsj: varchar 可空 - 无说明
- tspx: varchar 可空 - 无说明
- sfyxsj: varchar 可空 - 无说明
- zgh: varchar 可空 - 无说明
- yyxtgxsj: datetime 可空 - 无说明


### t_aixl_js_gwxx

**表说明**: 教职工岗位信息_AI用

表名: t_aixl_js_gwxx
表说明: 教职工岗位信息_AI用
字段数量: 24

字段列表:
- zgh: varchar 可空 - 工号
- zyjszwm: varchar 可空 - 专业技术职务码
- zyjszw: varchar 可空 - 专业技术职务
- zyjszwjbm: varchar 可空 - 专业技术职务级别码
- zyjszwjb: varchar 可空 - 专业技术职务级别
- zyjszwpdrq: varchar 可空 - 专业技术职务评定日期
- xzzw: varchar 可空 - 行政职务
- xzzwjbm: varchar 可空 - 行政职务级别码
- xzzwjb: varchar 可空 - 行政职务级别
- xzzwrzrq: varchar 可空 - 行政职务任职日期
- rzdwbm: varchar 可空 - 行政职务任职单位编码
- rzdw: varchar 可空 - 任职单位
- xngwlbm: varchar 可空 - 校内岗位类别码
- xngwlb: varchar 可空 - 校内岗位类别
- xngwdjm: varchar 可空 - 校内岗位等级码
- xngwdj: varchar 可空 - 校内岗位等级
- xngwdcm: varchar 可空 - 校内岗位档次码
- xngwdc: varchar 可空 - 校内岗位档次
- xngwrzrq: varchar 可空 - 校内岗位任职日期
- sygdjm: varchar 可空 - 事业岗位等级码
- sygwdj: varchar 可空 - 事业岗位等级
- sygprsj: varchar 可空 - 事业岗位聘任时间
- syglbm: varchar 可空 - 事业岗类别码
- syglb: varchar 可空 - 事业岗类别


### t_aixl_js_jbxx

**表说明**: 教师基本信息

表名: t_aixl_js_jbxx
表说明: 教师基本信息
字段数量: 107

字段列表:
- wid: varchar 可空 - 职工号
- zgh: varchar 可空 - 职工号
- xm: varchar 可空 - 姓名
- xmpy: varchar 可空 - 姓名拼音
- cym: varchar 可空 - 曾用名
- xbdm: varchar 可空 - 性别代码
- xb: varchar 可空 - 性别
- csrq: varchar 可空 - 出生日期
- jgdm: varchar 可空 - 籍贯代码
- jg: varchar 可空 - 籍贯
- csddm: varchar 可空 - 出生地
- csd: varchar 可空 - 出生地代码
- gjdqdm: varchar 可空 - 国家(地区)代码
- gjdq: varchar 可空 - 国家(地区)
- sfzjlxdm: varchar 可空 - 身份证件类型代码
- sfzjlx: varchar 可空 - 身份证件类型
- gatqdm: varchar 可空 - 港澳台侨代码
- gatq: varchar 可空 - 港澳台侨
- cjrq: varchar 可空 - 从教年月
- dedpdm: varchar 可空 - 第二党派代码
- dedp: varchar 可空 - 第二党派
- dedprq: varchar 可空 - 第二党派日期
- bzlbdm: varchar 可空 - 编制类别代码
- bzlb: varchar 可空 - 编制类别
- jzglydm: varchar 可空 - 教职工来源代码
- jzgly: varchar 可空 - 教职工来源
- hkszd: varchar 可空 - 户口所在地
- yrfsdm: varchar 可空 - 用人方式代码
- yrfs: varchar 可空 - 用人方式
- newdqztdm: varchar 可空 - 新当前状态代码
- newdqztmc: varchar 可空 - 新当前状态名称
- byxx: varchar 可空 - 毕业学校
- sxwrq: varchar 可空 - 授学位年月
- syxwdw: varchar 可空 - 授予学位单位
- jszgzh: varchar 可空 - 教师资格证号
- jszghdrq: varchar 可空 - 教师资格获得日期
- dslbdm: varchar 可空 - 导师类别代码
- dslb: varchar 可空 - 导师类别
- dsprrq: varchar 可空 - 导师聘任年月
- xklbdm: varchar 可空 - 学科类别代码
- xklb: varchar 可空 - 学科类别
- yjxkdm: varchar 可空 - 一级学科代码
- yjxk: varchar 可空 - 一级学科
- ejxkdm: varchar 可空 - 二级学科代码
- ejxk: varchar 可空 - 二级学科
- yjfx: varchar 可空 - 研究方向
- grjsgzdm: varchar 可空 - 工人技术工种代码
- grjsgz: varchar 可空 - 工人技术工种
- grjsdjpdrq: varchar 可空 - 工人技术等级评定年月
- gqgwdjdm: varchar 可空 - 工勤岗位等级代码
- gqgwdj: varchar 可空 - 工勤岗位等级
- gqgwprrq: varchar 可空 - 工勤岗位聘任日期
- sfsjt: varchar 可空 - 是否双肩挑
- sfsjtmc: varchar 可空 - 是否双肩挑名称
- sjtszdwdm: varchar 可空 - 双肩挑所在单位代码
- sjtszdw: varchar 可空 - 双肩挑所在单位
- mzdm: varchar 可空 - 民族代码
- mz: varchar 可空 - 民族
- sfzjh: varchar 可空 - 身份证件号
- jkzkdm: varchar 可空 - 健康状况代码
- jkzk: varchar 可空 - 健康状况
- hyzkdm: varchar 可空 - 婚姻状况代码
- hyzk: varchar 可空 - 婚姻状况
- cjgzrq: varchar 可空 - 参加工作年月
- lxrq: varchar 可空 - 来校年月
- zzmmdm: varchar 可空 - 政治面貌代码
- zzmm: varchar 可空 - 政治面貌
- cjdprq: varchar 可空 - 参加党派日期
- szdwdm: varchar 可空 - 所在单位代码
- szdw: varchar 可空 - 所在单位
- dqztdm: varchar 可空 - 当前状态代码（未使用）
- zgxldm: varchar 可空 - 最高学历代码
- zgxl: varchar 可空 - 最高学历
- byrq: varchar 可空 - 毕业年月
- zgxwdm: varchar 可空 - 最高学位代码
- zgxw: varchar 可空 - 最高学位
- grjsdjdm: varchar 可空 - 工人技术等级代码
- rylb: char 可空 - 人员类别
- sfzx: float 可空 - 是否在校
- zbqk: varchar 可空 - 在编情况
- jzgztmc: varchar 可空 - 教职工状态名称
- jzgrylb: varchar 可空 - 教职工人员类别
- sxzy: varchar 可空 - 所学专业
- czrq: datetime 可空 - 操作日期
- zyjszwm: varchar 可空 - 专业技术职务码
- zyjszw: varchar 可空 - 专业技术职务
- zyjszwjbm: varchar 可空 - 专业技术职务级别码
- zyjszwjb: varchar 可空 - 专业技术职务级别
- zyjszwpdrq: varchar 可空 - 专业技术职务评定日期
- xzzw: varchar 可空 - 行政职务
- xzzwjbm: varchar 可空 - 行政职务级别码
- xzzwjb: varchar 可空 - 行政职务级别
- xzzwrzrq: varchar 可空 - 行政职务任职日期
- rzdwbm: varchar 可空 - 行政职务任职单位编码
- rzdw: varchar 可空 - 任职单位
- xngwlbm: varchar 可空 - 校内岗位类别码
- xngwlb: varchar 可空 - 校内岗位类别
- xngwdjm: varchar 可空 - 校内岗位等级码
- xngwdj: varchar 可空 - 校内岗位等级
- xngwdcm: varchar 可空 - 校内岗位档次码
- xngwdc: varchar 可空 - 校内岗位档次
- xngwrzrq: varchar 可空 - 校内岗位任职日期
- sygdjm: varchar 可空 - 事业岗位等级码
- sygwdj: varchar 可空 - 事业岗位等级
- sygprsj: varchar 可空 - 事业岗位聘任时间
- syglbm: varchar 可空 - 事业岗类别码
- syglb: varchar 可空 - 事业岗类别


### t_aixl_js_jbxx2

**表说明**: 教师基本信息备份

表名: t_aixl_js_jbxx2
表说明: 教师基本信息备份
字段数量: 86

字段列表:
- wid: varchar 可空 - 职工号
- zgh: varchar 可空 - 职工号
- xm: varchar 可空 - 姓名
- xmpy: varchar 可空 - 姓名拼音
- cym: varchar 可空 - 曾用名
- xbdm: varchar 可空 - 性别代码
- xb: varchar 可空 - 性别
- csrq: varchar 可空 - 出生日期
- jgdm: varchar 可空 - 籍贯代码
- jg: varchar 可空 - 籍贯
- csddm: varchar 可空 - 出生地
- csd: varchar 可空 - 出生地代码
- gjdqdm: varchar 可空 - 国家(地区)代码
- gjdq: varchar 可空 - 国家(地区)
- sfzjlxdm: varchar 可空 - 身份证件类型代码
- sfzjlx: varchar 可空 - 身份证件类型
- gatqdm: varchar 可空 - 港澳台侨代码
- gatq: varchar 可空 - 港澳台侨
- cjrq: varchar 可空 - 从教年月
- dedpdm: varchar 可空 - 第二党派代码
- dedp: varchar 可空 - 第二党派
- dedprq: varchar 可空 - 第二党派日期
- bzlbdm: varchar 可空 - 编制类别代码
- bzlb: varchar 可空 - 编制类别
- jzglydm: varchar 可空 - 教职工来源代码
- jzgly: varchar 可空 - 教职工来源
- hkszd: varchar 可空 - 户口所在地
- yrfsdm: varchar 可空 - 用人方式代码
- yrfs: varchar 可空 - 用人方式
- newdqztdm: varchar 可空 - 新当前状态代码
- newdqztmc: varchar 可空 - 新当前状态名称
- byxx: varchar 可空 - 毕业学校
- sxwrq: varchar 可空 - 授学位年月
- syxwdw: varchar 可空 - 授予学位单位
- jszgzh: varchar 可空 - 教师资格证号
- jszghdrq: varchar 可空 - 教师资格获得日期
- dslbdm: varchar 可空 - 导师类别代码
- dslb: varchar 可空 - 导师类别
- dsprrq: varchar 可空 - 导师聘任年月
- xklbdm: varchar 可空 - 学科类别代码
- xklb: varchar 可空 - 学科类别
- yjxkdm: varchar 可空 - 一级学科代码
- yjxk: varchar 可空 - 一级学科
- ejxkdm: varchar 可空 - 二级学科代码
- ejxk: varchar 可空 - 二级学科
- yjfx: varchar 可空 - 研究方向
- grjsgzdm: varchar 可空 - 工人技术工种代码
- grjsgz: varchar 可空 - 工人技术工种
- grjsdjpdrq: varchar 可空 - 工人技术等级评定年月
- gqgwdjdm: varchar 可空 - 工勤岗位等级代码
- gqgwdj: varchar 可空 - 工勤岗位等级
- gqgwprrq: varchar 可空 - 工勤岗位聘任日期
- xpgwdm: varchar 可空 - 校聘岗位代码
- xpgw: text 可空 - 校聘岗位
- sfsjt: varchar 可空 - 是否双肩挑
- sfsjtmc: varchar 可空 - 是否双肩挑名称
- sjtszdwdm: varchar 可空 - 双肩挑所在单位代码
- sjtszdw: varchar 可空 - 双肩挑所在单位
- mzdm: varchar 可空 - 民族代码
- mz: varchar 可空 - 民族
- sfzjh: varchar 可空 - 身份证件号
- jkzkdm: varchar 可空 - 健康状况代码
- jkzk: varchar 可空 - 健康状况
- hyzkdm: varchar 可空 - 婚姻状况代码
- hyzk: varchar 可空 - 婚姻状况
- cjgzrq: varchar 可空 - 参加工作年月
- lxrq: varchar 可空 - 来校年月
- zzmmdm: varchar 可空 - 政治面貌代码
- zzmm: varchar 可空 - 政治面貌
- cjdprq: varchar 可空 - 参加党派日期
- szdwdm: varchar 可空 - 所在单位代码
- szdw: varchar 可空 - 所在单位
- dqztdm: varchar 可空 - 当前状态代码（未使用）
- zgxldm: varchar 可空 - 最高学历代码
- zgxl: varchar 可空 - 最高学历
- byrq: varchar 可空 - 毕业年月
- zgxwdm: varchar 可空 - 最高学位代码
- zgxw: varchar 可空 - 最高学位
- grjsdjdm: varchar 可空 - 工人技术等级代码
- rylb: char 可空 - 人员类别
- sfzx: float 可空 - 是否在校
- zbqk: varchar 可空 - 在编情况
- jzgztmc: varchar 可空 - 教职工状态名称
- jzgrylb: varchar 可空 - 教职工人员类别
- sxzy: varchar 可空 - 所学专业
- czrq: datetime 可空 - 操作日期


### t_aixl_js_kh

**表说明**: 教工考核

表名: t_aixl_js_kh
表说明: 教工考核
字段数量: 30

字段列表:
- wid: varchar 非空 - 主键
- zgh: varchar 可空 - 职工号
- khmc: varchar 可空 - 考核名称
- khrq: varchar 可空 - 考核日期
- khlbdm: varchar 可空 - 考核类别代码
- khlbmc: varchar 可空 - 考核类别名称
- ksrq: varchar 可空 - 开始日期
- jsrq: varchar 可空 - 结束日期
- grxj: longblob 可空 - 个人小结
- khjlmc: varchar 可空 - 考核结论名称
- khjldm: varchar 可空 - 考核结论代码
- xjsfjs: float 可空 - 薪级是否晋升
- clrq: datetime 可空 - 处理日期
- czlx: varchar 可空 - 操作类型
- sjly: varchar 可空 - 数据来源
- by1: varchar 可空 - 备用1
- by2: varchar 可空 - 备用2
- khny: varchar 可空 - 考核年份
- khzzkcr: varchar 可空 - 无说明
- khcy: varchar 可空 - 无说明
- grzj: varchar 可空 - 无说明
- tspx: varchar 可空 - 特殊排序
- sfyxsj: varchar 可空 - 是否有效数据
- khjg: varchar 可空 - 无说明
- khcl: varchar 可空 - 无说明
- cpdf: varchar 可空 - 无说明
- khyj: varchar 可空 - 考核意见
- jlsj: varchar 可空 - 结果登记时间
- khjlsj: varchar 可空 - 记录时间
- yyxtgxsj: datetime 可空 - 无说明


### t_aixl_js_ky_cgjl

**表说明**: 教师科研奖励

表名: t_aixl_js_ky_cgjl
表说明: 教师科研奖励
字段数量: 13

字段列表:
- wid: varchar 非空 (主键) - 技术主键ID
- clrq: datetime 可空 - 处理日期
- czlx: varchar 可空 - 操作类型
- sjly: varchar 可空 - 数据来源
- by1: varchar 可空 - 备用1
- zgh: varchar 可空 - 职工号
- cgmc: varchar 可空 - 成果名称
- jlmc: varchar 可空 - 奖励名称
- sjdj: varchar 可空 - 授奖等级
- hjrq: datetime 可空 - 获奖日期
- brpm: varchar 可空 - 本人排名
- xklx: varchar 可空 - 学科类型
- hjdj: varchar 可空 - 获奖等级


### t_aixl_js_ky_dmmc

**表说明**: 代码表

表名: t_aixl_js_ky_dmmc
表说明: 代码表
字段数量: 14

字段列表:
- wid: varchar 可空 - 记录编号
- clrq: datetime 可空 - 处理日期
- czlx: varchar 可空 - 操作类型
- sjly: varchar 可空 - 数据来源
- by1: varchar 可空 - 备用字段1
- dmmc: varchar 可空 - 代码名称
- dmlx: varchar 可空 - 代码类型
- dmlb: varchar 可空 - 代码类别
- dmid: varchar 可空 - 代码ID
- zdmid: varchar 可空 - 子代码ID
- zdm: varchar 可空 - 子代码
- dmsm: varchar 可空 - 代码说明
- zdmmc: varchar 可空 - 子代码名称
- px: varchar 可空 - 排序


### t_aixl_js_ky_xm

**表说明**: 教师科研项目

表名: t_aixl_js_ky_xm
表说明: 教师科研项目
字段数量: 20

字段列表:
- wid: varchar 可空 - 技术主键ID
- clrq: datetime 可空 - 处理日期
- czlx: varchar 可空 - 操作类型
- sjly: varchar 可空 - 数据来源
- by1: varchar 可空 - 备用1
- zgh: varchar 可空 - 职工号
- xmmc: varchar 可空 - 项目名称
- xmly: varchar 可空 - 项目来源
- xmdj: varchar 可空 - 项目等级
- xmjf: varchar 可空 - 项目经费
- dzjf: varchar 可空 - 到账经费
- xmkssj: datetime 可空 - 项目开始时间
- xmjssj: datetime 可空 - 项目结束时间
- sfjt: varchar 可空 - 是否结题
- jtsj: datetime 可空 - 结题时间
- pm: varchar 可空 - 排名
- lxsj: datetime 可空 - 立项时间
- xklx: varchar 可空 - 学科类型
- xmlydw: varchar 可空 - 项目来源单位
- xmfl: varchar 可空 - 项目分类


### t_aixl_js_ky_xslw

**表说明**: 教师学术论文

表名: t_aixl_js_ky_xslw
表说明: 教师学术论文
字段数量: 14

字段列表:
- wid: varchar 可空 - 技术主键ID
- clrq: datetime 可空 - 处理日期
- czlx: varchar 可空 - 操作类型
- sjly: varchar 可空 - 数据来源
- by1: varchar 可空 - 备用1
- zgh: varchar 可空 - 职工号
- lwmc: varchar 可空 - 论文名称
- fbkw: varchar 可空 - 发表刊物
- lwjsslqk: varchar 可空 - 论文检索收录情况
- kwjb: varchar 可空 - 刊物级别
- fbrq: datetime 可空 - 发表日期
- brpm: varchar 可空 - 本人排名
- xklx: varchar 可空 - 学科类型
- jslx: varchar 可空 - 角色类型


### t_aixl_js_ky_zl

**表说明**: 教师专利

表名: t_aixl_js_ky_zl
表说明: 教师专利
字段数量: 11

字段列表:
- wid: varchar 可空 - 技术主键ID
- clrq: datetime 可空 - 处理日期
- czlx: varchar 可空 - 操作类型
- sjly: varchar 可空 - 数据来源
- by1: varchar 可空 - 备用1
- zgh: varchar 可空 - 职工号
- zlmc: varchar 可空 - 专利名称
- zlsqh: varchar 可空 - 专利授权号
- sqsj: datetime 可空 - 授权时间
- brpm: varchar 可空 - 本人排名
- xklx: varchar 可空 - 学科类型


### t_aixl_js_zyjszw

表名: t_aixl_js_zyjszw
字段数量: 36

字段列表:
- wid: varchar 可空 - 无说明
- zgh: varchar 可空 - 无说明
- zyjszwdm: varchar 可空 - 无说明
- zyjszwjbdm: varchar 可空 - 无说明
- zyjszwpdrq: varchar 可空 - 无说明
- psdw: varchar 可空 - 无说明
- zsbh: varchar 可空 - 无说明
- qdzgtj: varchar 可空 - 无说明
- przyjszwdm: varchar 可空 - 无说明
- przyjszwjbdm: varchar 可空 - 无说明
- spdwdm: varchar 可空 - 无说明
- prqsrq: varchar 可空 - 无说明
- przzrq: varchar 可空 - 无说明
- pzwh: varchar 可空 - 无说明
- przt: varchar 可空 - 无说明
- jprq: varchar 可空 - 无说明
- jpyy: varchar 可空 - 无说明
- clrq: datetime 可空 - 无说明
- czlx: varchar 可空 - 无说明
- sjly: varchar 可空 - 无说明
- by1: varchar 可空 - 无说明
- by2: varchar 可空 - 无说明
- rzzgmcm: varchar 可空 - 无说明
- dz_zwlb: varchar 可空 - 无说明
- dz_qdzgtj: varchar 可空 - 无说明
- dz_tjzcrzqssj: varchar 可空 - 无说明
- dz_xklb: varchar 可空 - 无说明
- dz_xxnpzc: varchar 可空 - 无说明
- dz_sjwh: varchar 可空 - 无说明
- dz_xxwh: varchar 可空 - 无说明
- dz_yhzc: varchar 可空 - 无说明
- dz_prdw: varchar 可空 - 聘任单位
- dz_tspx: varchar 可空 - 特殊排序
- dz_sfyxsj: varchar 可空 - 是否有效数据
- dz_jlsj: varchar 可空 - 记录时间
- yyxtgxsj: datetime 可空 - 无说明


### t_aixl_xsdjksxx

**表说明**: 学生等级考试信息_AI

表名: t_aixl_xsdjksxx
表说明: 学生等级考试信息_AI
字段数量: 19

字段列表:
- wybs: varchar 可空 - 唯一标识
- xh: varchar 可空 - 学生学号
- xszjh: varchar 可空 - 学生证件号
- xszkzh: varchar 可空 - 学生准考证号
- xsxm: varchar 可空 - 学生姓名
- xslx: varchar 可空 - 学生类型
- xspyccm: varchar 可空 - 学生培养层次码
- szxym: varchar 可空 - 所在学院码
- szzym: varchar 可空 - 所在专业码
- djksmc: varchar 可空 - 等级考试名称
- djkslxm: varchar 可空 - 等级考试类型码
- djkscj: varchar 可空 - 等级考试成绩
- djkscj2: varchar 可空 - 等级考试成绩2
- ksrq: varchar 可空 - 考试日期
- xnxq: varchar 可空 - 学年学期
- sfqk: varchar 可空 - 是否缺考
- gxsj: varchar 可空 - 更新时间
- tstamp: varchar 可空 - 时间戳
- sfrzh: varchar 可空 - 身份认证号


### t_aixl_xsfxzyxx

**表说明**: 学生辅修专业信息

表名: t_aixl_xsfxzyxx
表说明: 学生辅修专业信息
字段数量: 10

字段列表:
- wybs: varchar 可空 - 唯一标识
- xh: varchar 可空 - 学号
- xm: varchar 可空 - 姓名
- zybm: varchar 可空 - 专业编码
- zymc: varchar 可空 - 专业名称
- bjbm: varchar 可空 - 班级编码
- nj: varchar 可空 - 年级
- gxsj: varchar 可空 - 更新时间
- tstamp: varchar 可空 - 时间戳
- sfrzh: varchar 可空 - 身份认证号


### t_aixl_xskjjsjhjxx

**表说明**: 学生科技竞赛及获奖信息

表名: t_aixl_xskjjsjhjxx
表说明: 学生科技竞赛及获奖信息
字段数量: 13

字段列表:
- ssdj: varchar 可空 - 赛事等级
- ssmc: varchar 可空 - 赛事名称
- jslb: varchar 可空 - 教师列表
- xslb: varchar 可空 - 学生列表
- zbdwxx: varchar 可空 - 主办单位信息
- xsszxymc: varchar 可空 - 学生所在学院名称
- jsszxymc: varchar 可空 - 教师所在学院名称
- ssjb: varchar 可空 - 赛事级别
- rylb: varchar 可空 - 人员类别
- hjdj: varchar 可空 - 获奖等级
- hjnf: varchar 可空 - 获奖年份
- ssdd: varchar 可空 - 赛事地点
- tstamp: varchar 可空 - 时间戳


### t_aixl_xskjjsjhjxx_copy1

**表说明**: 学生科技竞赛及获奖信息

表名: t_aixl_xskjjsjhjxx_copy1
表说明: 学生科技竞赛及获奖信息
字段数量: 13

字段列表:
- ssdj: varchar 可空 - 赛事等级
- ssmc: varchar 可空 - 赛事名称
- jslb: varchar 可空 - 教师列表
- xslb: varchar 可空 - 学生列表
- zbdwxx: varchar 可空 - 主办单位信息
- xsszxymc: varchar 可空 - 学生所在学院名称
- jsszxymc: varchar 可空 - 教师所在学院名称
- ssjb: varchar 可空 - 赛事级别
- rylb: varchar 可空 - 人员类别
- hjdj: varchar 可空 - 获奖等级
- hjnf: varchar 可空 - 获奖年份
- ssdd: varchar 可空 - 赛事地点
- tstamp: varchar 可空 - 时间戳


### t_aixl_zxbz_gwlxbz

表名: t_aixl_zxbz_gwlxbz
字段数量: 7

字段列表:
- wid: varchar 可空 - 无说明
- clrq: datetime 可空 - 无说明
- czlx: varchar 可空 - 无说明
- sjly: varchar 可空 - 无说明
- by1: varchar 可空 - 无说明
- dm: varchar 可空 - 无说明
- mc: varchar 可空 - 无说明


### t_aixl_zxbz_zwlb

表名: t_aixl_zxbz_zwlb
字段数量: 15

字段列表:
- wid: varchar 可空 - 无说明
- dm: varchar 可空 - 无说明
- mc: varchar 可空 - 无说明
- px: float 可空 - 无说明
- sfsy: float 可空 - 无说明
- fbqk: float 可空 - 无说明
- ybzdm: varchar 可空 - 无说明
- qssyrq: datetime 可空 - 无说明
- zzsyrq: datetime 可空 - 无说明
- bzly: varchar 可空 - 无说明
- sjly: varchar 可空 - 无说明
- by2: varchar 可空 - 无说明
- czlx: varchar 可空 - 无说明
- by1: varchar 可空 - 无说明
- clrq: datetime 可空 - 无说明


### t_aixl_zxbz_zyjszw

表名: t_aixl_zxbz_zyjszw
字段数量: 21

字段列表:
- wid: varchar 非空 - 无说明
- dm: varchar 可空 - 无说明
- mc: varchar 可空 - 无说明
- lbdm: varchar 可空 - 无说明
- cc: varchar 可空 - 无说明
- ls: varchar 可空 - 无说明
- px: varchar 可空 - 无说明
- sfsy: varchar 可空 - 无说明
- fbqk: varchar 可空 - 无说明
- ybzdm: varchar 可空 - 无说明
- qssyrq: datetime 可空 - 无说明
- zzsyrq: datetime 可空 - 无说明
- bzly: varchar 可空 - 无说明
- clrq: datetime 可空 - 无说明
- czlx: varchar 可空 - 无说明
- sjly: varchar 可空 - 无说明
- by1: varchar 可空 - 无说明
- by2: varchar 可空 - 无说明
- jbdm: varchar 可空 - 无说明
- jbmc: varchar 可空 - 无说明
- ywmc: varchar 可空 - 无说明


### users

表名: users
字段数量: 5

字段列表:
- id: int 非空 (主键) - 无说明
- username: varchar 非空 (唯一键) - 无说明
- password: varchar 非空 - 无说明
- email: varchar 非空 (唯一键) - 无说明
- created_at: datetime 可空 - 无说明


