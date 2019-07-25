import requests
import json
import os
import random
from py2neo import Graph
from inhekbnew.redisutil import Redis
from inhekbnew.redis_service import redis_query_relations_entity

DEBUG = False
API = 'http://192.168.3.156:32033'

class Question:
    def __init__(self, question_id, question_title, question_entity, question_type,
        question_options=None,other=False,note="",location=""):
        #问题的id
        self.id = question_id
        #问题的题面
        self.title = question_title
        #问题对应的医学实体,也就是对应的逻辑变量名
        self.entity = question_entity
        #问题的类型
        self.type = question_type
        #问题选项列表
        self.options = question_options
        #问题是否开启‘其他’选项
        self.other = other
        #问题的补充说明
        self.note = note
        #如果问题是部位选择时,该属性表示被选部分的代码
        self.location = location


class Answer:
    def __init__(self, question_id, options):
        #该答案对应问题的id
        self.question_id = question_id
        #患者选择的选项  
        self.options = options


class QuestionGenerator:
    def __init__(self, variable_to_entity_dict):
        '''
        类的构造函数
        :param variable_to_entity_dict:dict类型,是逻辑变量名到kb实体名的映射,逻辑内核调用生成器
        模块的时候传入
        '''
        self.variable_to_entity_dict = variable_to_entity_dict
        self.variable_to_entity_dict['自主输入'] = '自主输入'
        self.variable_to_entity_dict['文件上传'] = '文件上传'
        self.entity_to_variable_dict = {}
        for k, v in variable_to_entity_dict.items():
            self.entity_to_variable_dict[v] = k
        self.questionsMapList = {}
        basepath = os.path.abspath(__file__)
        folder = os.path.dirname(basepath)
        data_path = os.path.join(folder, 'questionsMapList.csv')
        with open(data_path, 'r', encoding='utf-8') as f:
            content = f.readlines()
            for c in content:
                c = c.strip()
                c = c.split('\t')
                self.questionsMapList[c[0]] = c[1:]
        # if DEBUG:
        #     print('QuestionGenerator.__init__', self.questionsMapList)
        self.questionID = 1
        self.questions = {}
        self.answers = {}
        self.need_ask_more = {}

    def _get_type(self, s:str):
        '''
        获得s在KB中的类型
        :param s:变量对应的名称
        '''
        # if DEBUG:
        #     print('QuestionGenerator._get_type', self._post_downwardRecursion({'entity':s})['type'])
        s_r_o = self._post_downwardRecursion({'entity':s})
        return s_r_o['type'] if 'type' in s_r_o else None

    def _post_downwardRecursion(self, body:dict) -> dict:
        '''
        发送报文获得三元组
        :param body:dict类型，报文的body
        :return 返回response.text的dict
        '''
        url = API + '/downwardRecursion'
        response = requests.post(url, data = json.dumps(body))
        # if DEBUG:
        #     print('QuestionGenerator._post_downwardRecursion', type(response.text), response)
        return json.loads(response.text)

    def __in_check_need_symptom(self, symptom:str) -> bool:
        '''
        查询检查症状对应表
        :return 返回是否在表里
        '''
        random_num = random.randrange(0, 10)
        if random_num < 2:
            return True
        else:
            return False

    def __is_subjective_sensation(self, symptom:str) -> bool:
        '''
        查询KB询问是否主观可感
        '''
        random_num = random.randrange(0, 10)
        if random_num < 8:
            return True
        else:
            return False

    def __get_check_by_symptom(self, symptom:str) -> str:
        '''
        根据症状获得需要做的检查
        '''
        inbox_check = ['身高', '体重', '血压', '血氧', '体温']
        outbox_check = ['血生化检查', '实验室检查', 'B超检查', 'CT检查', 'B超', '膀胱镜', '病理性U波心电图', '心电图', '肛门指诊', '膀胱镜下取活检', '膀胱镜检查', '血液实验室的检查', '腰骶椎X线片', '尿道造影', '尿道造影检查', '细菌培养', '常规检查', '体重指数', 'BMI', '尿液镜检', '显微镜检查', '支气管镜检', '免疫学检测', '隐血试验', '镜检', '尿三杯试验', '影像学检查', '肝穿刺活组织检查', '血清学试验', '胆红素定性试验', '尿常规', '逆行胰胆管造影', '腹腔镜检查', '磁共振胰胆管成像', '非介入性胰胆管成像技术', '198金或99锝肝扫描', '131碘玫瑰红扫描', '肝穿刺活检', '上腹部CT扫描', '经皮肝穿刺胆道造影', 'X线胆道造影', 'X线检查腹部平片', 'ERCP', 'PTC', 'MRCP', '鼻咽镜检查', '普萘洛尔（心得安）试验', '正常心电图', '体格检查', '辅助检查', '后腰椎穿刺', '腰椎穿刺', '后腰椎麻醉', '腰椎麻醉', '分光镜检查']
        random_num = random.randrange(0, len(inbox_check) + len(outbox_check))
        if random_num < 5:
            return inbox_check[random_num]
        else:
            return outbox_check[random_num - 5]

    def generateQuestionsbyLogicVaribales(self, logic_variable_list):
        '''
        :param logic_variable_list:list类型,list内是一个个字符串,表示逻辑变量的名字
        '''
        ###分析logic_variable_list来生成对应的问题
        '''
        问题实例,主要就是返回一个包含一个或多个问题实例的列表(当前阶段一般一个list中只有一个Question实
        例),Question类的定义附在后面,生成器模块内部定义一下Question类
        '''
        if logic_variable_list is None or len(logic_variable_list) == 0:
            raise AssertionError('logic_variable_list is None or len(logic_variable_list) == 0')
        
        entity_list = [''] * len(logic_variable_list)
        for i in range(len(logic_variable_list)):
            entity_list[i] = self.variable_to_entity_dict[logic_variable_list[i]]

        if len(entity_list) == 1:
            if entity_list[0] == '自主输入':
                q = Question(
                    question_id = self.questionID,
                    question_title = '自主输入测试',
                    question_entity = '自主输入',
                    question_type = 3 #3是自主输入的问题类型编号
                )
                self.questions[self.questionID] = q
                self.questionID += 1
                return q
            elif entity_list[0] == '文件上传':
                q = Question(
                    question_id = self.questionID,
                    question_title = '文件上传测试',
                    question_entity = '文件上传',
                    question_type = 4 #4是文件上传的问题类型编号
                )
                self.questions[self.questionID] = q
                self.questionID += 1
                return q
            else:
                variable_type = self._get_type(entity_list[0]) 
                if variable_type is None:
                    raise AssertionError('can not find variable {}\'s type '.format(entity_list[0]))
                if variable_type == '症状':
                    # 主诉 单选题
                    if __in_check_need_symptom(entity_list[0]):
                        ### 去做检查
                        check = __get_check_by_symptom(entity_list[0])
                        if check in ['身高', '体重', '血压', '血氧', '体温']:
                            ### 查体题 即 舱内检查
                            # 舱内检查只有 ['身高', '体重', '血压', '血氧', '体温']
                            random_num = random.randrange(0, len(self.questionsMapList[variable_type])) #随机选择第几个问题
                            title = self.questionsMapList[variable_type][random_num].format(entity_list[0])
                            q = Question(
                                question_id = self.questionID,
                                question_title = title,
                                question_entity = entity_list[0],
                                question_type = 6,
                                question_options = [{'num':1,'value':'是'},{'num':2,'value':'否'}]
                            )
                            if DEBUG:
                                print(title)
                                print(q.__dict__)
                            self.questions[self.questionID] = q
                            self.questionID += 1
                            return q
                        else:
                            ### 检查题 即 舱外检查 包含除舱内检查外的检查
                            random_num = random.randrange(0, len(self.questionsMapList[variable_type])) #随机选择第几个问题
                            title = self.questionsMapList[variable_type][random_num].format(entity_list[0])
                            q = Question(
                                question_id = self.questionID,
                                question_title = title,
                                question_entity = entity_list[0],
                                question_type = 7,
                                question_options = [{'num':1,'value':'是'},{'num':2,'value':'否'}]
                            )
                            if DEBUG:
                                print(title)
                                print(q.__dict__)
                            self.questions[self.questionID] = q
                            self.questionID += 1
                            return q
                    elif __is_subjective_sensation(entity_list[0]):
                        ### 主观可感 
                        random_num = random.randrange(0, len(self.questionsMapList[variable_type])) #随机选择第几个问题
                        title = self.questionsMapList[variable_type][random_num].format(entity_list[0])
                        q = Question(
                            question_id = self.questionID,
                            question_title = title, 
                            question_entity = entity_list[0],
                            question_type = 1,
                            question_options = [{'num':1,'value':'是'},{'num':2,'value':'否'}]
                        )
                        if DEBUG:
                            print(title)
                            print(q.__dict__)
                        self.questions[self.questionID] = q
                        self.need_ask_more.add(self.questionID)
                        self.questionID += 1
                        return q
                    else:
                        raise AssertionError('Variable {} can\'t find in check_need_symptom_list, and it can\'t be subjective sensation! '.format(entity_list[0]))
                elif variable_type in ['疾病', '检查', '病史', '事件', '化学物质', '食品']:
                    random_num = random.randrange(0, len(self.questionsMapList[variable_type])) #随机选择第几个问题
                    title = self.questionsMapList[variable_type][random_num].format(entity_list[0])
                    q = Question(
                        question_id = self.questionID,
                        question_title = title,
                        question_entity = entity_list[0],
                        question_type = 1,
                        question_options = [{'num':1,'value':'是'},{'num':2,'value':'否'}]
                    )
                    if DEBUG:
                        print(title)
                        print(q.__dict__)
                    self.questions[self.questionID] = q
                    self.need_ask_more.add(self.questionID)
                    self.questionID += 1
                    return q
                elif variable_type in ['修饰语', '部位', '否定词', '生物', '时间', '数据', '生理概念', '病理概念']:
                    raise AssertionError('Variable {}\'s type is {}, it can\'t be asked! '.format(entity_list[0], variable_type))
                elif variable_type in ['年龄', '人群分类']:
                    raise AssertionError('Variable {}\'s type is {}, it can\'t be asked! '.format(entity_list[0], variable_type))
                elif variable_type == '嵌套实体':
                    pass
        elif len(entity_list) > 1:
            # 多选题
            title = '请您在下列选项中选择您所出现的症状。'
            options = [{'num':i+1,'value':entity_list[i]} for i in range(len(entity_list))]
            options.append[{'num': len(entity_list), 'value': '都没有'}]
            q = Question(
                question_id = self.questionID,
                question_title = title,
                question_entity = entity_list,
                question_type = 2,
                question_options = options
            )
            if DEBUG:
                print(title)
                print(q.__dict__)
            self.questions[self.questionID] = q
            self.questionID += 1
            return q

    def determineValueofLogicVariables(self, answer):
        '''
        :param answer:list类型,list内是一个个Answer的实例(当前阶段一个这个list中一般只有一个
        Answer实例),Answer类的定义附在后面,生成器模块内部定义一下Answer类
        '''
        ### 如果需要继续问更详细的问题则返回一个Question 否则
        ### 分析answer来给逻辑变量赋值
        ### 逻辑变量的取值列表,列表内是一个个二元的tuple,tuple[0]表示逻辑变量,tuple[1]表示逻辑变量的
        ### 取值(1表示True,0表示False,2表示未知)
        self.answers[answer.question_id] = answer
        question = self.questions[answer.question_id]
        entity = self.questions[answer.question_id].entity

        variable_value_list = []
        if type(entity) == list: 
            #多选题 entity = ['发热','咳嗽']
            options_values = [answer.options[i]['value'] for i in range(len(answer.options))]
            for e in entity:
                if e in options_values:
                    variable = self.entity_to_variable_dict[e]
                    variable_value_list.append((variable, 1))
                else:
                    variable = self.entity_to_variable_dict[e]
                    variable_value_list.append((variable, 0))
        elif type(entity) == str: 
            #单选题 entity = '发热'
            if answer.options[0]['num'] == 1:
                variable = self.entity_to_variable_dict[entity]
                variable_value_list.append((variable, 1))
            else:
                variable = self.entity_to_variable_dict[entity]
                variable_value_list.append((variable, 0))
            # variable_value_list = [('发热',1)]
            if answer.question_id in self.need_ask_more:
                if '时间' in self.need_ask_more[answer.question_id]:
                    random_num = random.randrange(0, len(self.questionsMapList['时间'])) #随机选择第几个问题
                    title = self.questionsMapList['时间'][random_num].format(entity)
                    q = Question(
                        question_id = self.questionID,
                        question_title = title,
                        question_entity = variable_value_list[0],
                        question_type = 1,
                        question_options = [{'num': 1,'value': 0, 'note': '日', 'dynamic': {'min': 0, 'max': 30, 'step': 1, 'metric': '日'}}, 
                            {'num': 2,'value': 0, 'note': '月', 'dynamic': {'min': 0, 'max': 12, 'step': 1, 'metric': '月'}}, 
                            {'num': 3, 'value': 0, 'note': '年', 'dynamic': {'min': 0, 'max': 30, 'step': 1, 'metric': '年'}}]
                    )
                    if DEBUG:
                        print(title)
                        print(q.__dict__)
                    self.questions[self.questionID] = q
                    self.questionID += 1
                    return q
                elif '部位' in self.need_ask_more[answer.question_id]:
                    random_num = random.randrange(0, len(self.questionsMapList['部位'])) #随机选择第几个问题
                    title = self.questionsMapList['部位'][random_num].format(entity)
                    q = Question(
                        question_id = self.questionID,
                        question_title = title,
                        question_entity = variable_value_list[0],
                        question_type = 1,
                        location = 'G'
                    )
                    if DEBUG:
                        print(title)
                        print(q.__dict__)
                    self.questions[self.questionID] = q
                    self.questionID += 1
                    return q
        elif type(entity) == tuple:
            if answer.question_id in self.need_ask_more:
                if '时间' in self.need_ask_more[answer.question_id]:
                    random_num = random.randrange(0, len(self.questionsMapList['时间'])) #随机选择第几个问题
                    title = self.questionsMapList['时间'][random_num].format(entity)
                    q = Question(
                        question_id = self.questionID,
                        question_title = title,
                        question_entity = entity,
                        question_type = 1,
                        question_options = [{'num': 1,'value': 0, 'note': '日', 'dynamic': {'min': 0, 'max': 30, 'step': 1, 'metric': '日'}}, 
                            {'num': 2,'value': 0, 'note': '月', 'dynamic': {'min': 0, 'max': 12, 'step': 1, 'metric': '月'}}, 
                            {'num': 3, 'value': 0, 'note': '年', 'dynamic': {'min': 0, 'max': 30, 'step': 1, 'metric': '年'}}]
                    )
                    if DEBUG:
                        print(title)
                        print(q.__dict__)
                    self.questions[self.questionID] = q
                    self.questionID += 1
                    return q
                elif '部位' in self.need_ask_more[answer.question_id]:
                    random_num = random.randrange(0, len(self.questionsMapList['部位'])) #随机选择第几个问题
                    title = self.questionsMapList['部位'][random_num].format(entity)
                    q = Question(
                        question_id = self.questionID,
                        question_title = title,
                        question_entity = entity,
                        question_type = 1,
                        location = 'G'
                    )
                    if DEBUG:
                        print(title)
                        print(q.__dict__)
                    self.questions[self.questionID] = q
                    self.questionID += 1
                    return q
            else:
                return [entity]
        if DEBUG:
            print(variable_value_list)
        return variable_value_list


if __name__ == "__main__":
    DEBUG = True
    questions = QuestionGenerator({'x1':'发热', 'x2':'咳嗽'})
    questions._post_downwardRecursion({'entity':'发热'})
    questions._get_type('发热')
    question_list = questions.generateQuestionsbyLogicVaribales(['x1', 'x2'])
    answer = Answer(question_list[0].id, [question_list[0].options[0]])
    questions.determineValueofLogicVariables([answer])
    question_list = questions.generateQuestionsbyLogicVaribales(['x2'])
    answer = Answer(question_list[0].id, [question_list[0].options[0]])
    questions.determineValueofLogicVariables([answer])