import requests
import json
import os
import random

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
        self.variable_to_entity_dict['部位选择'] = '部位选择'
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

    def generateQuestionsbyLogicVaribales(self, logic_variable_list):
        '''
        :param logic_variable_list:list类型,list内是一个个字符串,表示逻辑变量的名字
        '''
        ###分析logic_variable_list来生成对应的问题
        '''
        问题实例,主要就是返回一个包含一个或多个问题实例的列表(当前阶段一般一个list中只有一个Question实
        例),Question类的定义附在后面,生成器模块内部定义一下Question类
        '''
        # q = Question(
        #     question_id = 1,
        #     tite = '请问您是否有发热',
        #     question_entity = '发热',
        #     question_type = 1,
        #     question_options = [{'num':1,'value':'有'},{'num':2,'value':'否'}]
        # )
        # question_list = []
        # question_list.append(q)
        # return question_list
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
                question_list = []
                question_list.append(q)
                return question_list
            elif entity_list[0] == '文件上传':
                q = Question(
                    question_id = self.questionID,
                    question_title = '文件上传测试',
                    question_entity = '文件上传',
                    question_type = 4 #4是文件上传的问题类型编号
                )
                self.questions[self.questionID] = q
                self.questionID += 1
                question_list = []
                question_list.append(q)
                return question_list
            elif entity_list[0] == '部位选择':
                q = Question(
                    question_id = self.questionID,
                    question_title = '部位选择测试',
                    question_entity = '部位选择',
                    question_type = 5 #5是文件上传的问题类型编号
                )
                self.questions[self.questionID] = q
                self.questionID += 1
                question_list = []
                question_list.append(q)
                return question_list
            else:
                variable_type = self._get_type(entity_list[0]) 
                if variable_type is None:
                    raise AssertionError('can not find variable {}\'s type '.format(entity_list[0]))
                if variable_type in ['状态修饰语', '性质修饰语', '程度修饰语', '频率修饰语', '方位修饰语', '数量修饰语',\
                        '疾病', '症状', '部位', '否定词', '病史', '事件', '颜色', '生物', '时间', '化学物质', '食品', '年龄', '人群分类', '数据', '生理概念', '病理概念']:
                    # 主诉 单选题
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
                    self.questionID += 1
                    question_list = []
                    question_list.append(q)
                    return question_list
                elif variable_type in ['检查'] and entity_list[0] in ['身高', '体重', '血压', '血氧', '体温']:
                    # 查体题 即 舱内检查
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
                    question_list = []
                    question_list.append(q)
                    return question_list
                elif variable_type in ['检查']:
                    # 检查题 即 舱外检查 包含除舱内检查外的检查
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
                    question_list = []
                    question_list.append(q)
                    return question_list
        elif len(entity_list) > 1:
            # 多选题
            title = '请您在下列选项中选择您所出现的症状。'
            q = Question(
                question_id = self.questionID,
                question_title = title,
                question_entity = entity_list,
                question_type = 2,
                question_options = [{'num':i+1,'value':entity_list[i]} for i in range(len(entity_list))]
            )
            if DEBUG:
                print(title)
                print(q.__dict__)
            self.questions[self.questionID] = q
            self.questionID += 1
            question_list = []
            question_list.append(q)
            return question_list

    def determineValueofLogicVariables(self, answer_list):
        '''
        :param answer:list类型,list内是一个个Answer的实例(当前阶段一个这个list中一般只有一个
        Answer实例),Answer类的定义附在后面,生成器模块内部定义一下Answer类
        '''
        ### 分析answer来给逻辑变量赋值
        ### 逻辑变量的取值列表,列表内是一个个二元的tuple,tuple[0]表示逻辑变量,tuple[1]表示逻辑变量的
        ### 取值(1表示True,0表示False,2表示未知)
        variable_value_list = []
        for a in answer_list:
            entity = self.questions[a.question_id].entity
            if type(entity) == list: 
                #多选题 entity = ['发热','咳嗽']
                options_values = [a.options[i]['value'] for i in range(len(a.options))]
                for e in entity:
                    if e in options_values:
                        variable = self.entity_to_variable_dict[e]
                        variable_value_list.append((variable, 1))
                    else:
                        variable = self.entity_to_variable_dict[e]
                        variable_value_list.append((variable, 0))
            else: 
                #单选题 entity = '发热'
                if a.options[0]['num'] == 1:
                    variable = self.entity_to_variable_dict[entity]
                    variable_value_list.append((variable, 1))
                else:
                    variable = self.entity_to_variable_dict[entity]
                    variable_value_list.append((variable, 0))
        # variable_value_list = [('发热',1)]
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