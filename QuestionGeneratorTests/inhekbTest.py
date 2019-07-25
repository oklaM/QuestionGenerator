from py2neo import Graph
from inhekbnew.redisutil import Redis
from inhekbnew.redis_service import query_relations_entity_r
from inhekbnew.redis_service import query_entity_names_by_type_r
from inhekbnew.redis_service import query_entity_is_nested_r
from inhekbnew.redis_service import query_neighbours_r
from inhekbnew.redis_service import query_upward_recursion_r
from inhekbnew.redis_service import query_relations_entity

if __name__ == "__main__":

    # # 完整的连接:
    red = Redis(host='192.168.3.156', password="", port=32033, db=0, use_pool=False)
    graph = Graph(host='202.120.40.114',http_port=37474, user='neo4j', password='123', bolt=False)
    # red = Redis()
    # graph = Graph()
    result = query_neighbours_r(red, graph, "胸痛")
    print("头疼:")
    print(result)
    # 查询某类关系的所有实体
    result = query_relations_entity_r(red, graph, "转变为")
    print("转变为关系的实体：")
    print(result)
    # 查询某类型的所有实体
    result = query_entity_names_by_type_r(red, graph, "检查")
    print("否定词：")
    print(result)
    # 查询嵌套实体
    result = query_entity_is_nested_r(red, graph, "腰背部长期负重导致局部病变")
    print("腰背部长期负重导致局部病变：")
    print(result)
    # 查询一个节点所有连出的边
    result = query_neighbours_r(red, graph, "腰背部长期负重导致局部病变")
    print("腰背部长期负重导致局部病变：")
    print(result)
    # 查询一个三元组的上层嵌套实体的接口
    result = query_upward_recursion_r(red, graph, "66641ac0aa0d11e996492cfda1bc0bc5")
    print("66641ac0aa0d11e996492cfda1bc0bc5的上层嵌套实体：")
    print(result)