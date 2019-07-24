from QuestionGenerator.questions import QuestionGenerator, Answer, Question

q = QuestionGenerator({})
# 咳嗽
question_list = q.generateQuestionsbyLogicVaribales(['咳嗽'])
# (咳嗽, 1)
answer = Answer(question_list[0].id, [question_list[0].options[0]])
print(q.determineValueofLogicVariables([answer]))
# # (咳嗽, 0)
# answer = Answer(question_list[0].id, [question_list[0].options[1]])
# q.determineValueofLogicVariables([answer])
# 咽喉红肿
question_list = q.generateQuestionsbyLogicVaribales(['咽喉红肿'])
# # (咽喉红肿, 1)
# answer = Answer(question_list[0].id, [question_list[0].options[0]])
# q.determineValueofLogicVariables([answer])
# (咽喉红肿, 0)
answer = Answer(question_list[0].id, [question_list[0].options[1]])
print(q.determineValueofLogicVariables([answer]))
# '胸闷', '气短'
question_list = q.generateQuestionsbyLogicVaribales(['胸闷', '气短'])
question_list = q.generateQuestionsbyLogicVaribales(['自主输入'])
question_list = q.generateQuestionsbyLogicVaribales(['文件上传'])
question_list = q.generateQuestionsbyLogicVaribales(['部位选择'])