# KB接口设计

## I. 分类症状接口
为主引擎的查询分类症状接口提供服务。该接口调用频率极低，一般为前端更新数据时使用，因此查询效率要求不高。

### 路径
/symptoms

### Input
无

### Output
参见《主引擎API文档v1.3》，“返回分类症状”接口说明。

## II. 查询某类关系的所有实例的接口
查询某一类关系的所有三元组。

### 路径
/relationsByType

### Input
请求报文结构：
```json
{
    "type": <String>
}
```
其中：
```
字段	含义
type	查询的目标关系类型
```
例如：
```json
{
    "type": "导致"
}
```

### Output
返回报文结构：
```json
{
    "subjects": [<String>],
    "objects": [<String>]
}
```
其中：
```json
字段		含义
subjects	所有符合条件的三元组的主语序列，每一个元素与objects数组中同位置的元素属于同一个三元组。
objects		所有符合条件的三元组的宾语序列，每一个元素与subjects数组中同位置的元素属于同一个三元组。
```
例如：
```json
{
    "subjects": ["肺炎", "肺炎", "糖尿病"],
    "objects": ["发热", "咳嗽", "高血压"]
}
```

## III. 查询某类型的所有实体的接口
查询某一个类型的所有实体。

### 路径
/entitiesByType

### Input
请求报文结构
```json
{
    "type": <String>
}
```
其中：
```
字段	含义
type	查询的目标实体类型
```
例如：
```json
{
    "type": "疾病"
}
```

### Output
返回报文结构：
```json
{
    "entities": [<String>]
}
```
其中:
```
字段		含义
entities	所有符合条件的实体名称的列表。
```
例如：
```json
{
    "entities": ["肺炎", "艾滋病", "奥兹海默症"]
}
```

## IV. 查询实体是否为嵌套的接口
根据输入实体的名称确定实体是否还有更详细的下层嵌套结构

### 路径
/downwardRecursion

### Input
请求报文结构：
```json
{
    "entity": <String>
}
```
其中：
```
字段	含义
entity	查询的实体名称
```
例如：
```json
{
    "entity": "发热"
}
```

### Output
返回报文结构：
```json
{
    "name": <String>,
    "type": <String>,
    "subject": <Triple>,
    "predicate": <String>,
    "object": <Triple>
}
```
其中：
```
字段		含义
name		当前实体的名称
type		表示当前实体的类型
subject		如果当前实体具有嵌套结构，则表示嵌套结构中的主语实体，结构与当前报文结构相同（递归）；否则为空。
predicate	如果当前实体具有嵌套结构，则表示嵌套结构中的关系类型；否则为空
object		如果当前实体具有嵌套结构，则表示嵌套结构中的宾语实体，结构与当前报文结构相同（递归）；否则为空。
```
例如：
```json
{
    "name": "发热",
    "type": "症状",
    "subject": {
        "name": "体温升高",
        "type": "生理概念",
        "subject": {
            "name": "升高",
            "type": "程度修饰语"
        },
        "predicate": "修饰限定",
        "object": {
            "name": "体温",
            "type": "生理概念"
        }
    },
    "predicate": "条件为",
    "object": {
        "name": "正常范围超出",
        "type": "数据",
        "subject": {
            "name": "超出",
            "type": "程度修饰语"
        },
        "predicate": "修饰限定",
        "object": {
            "name": "正常范围",
            "type": "数据"
        }
    }
}
```

## V. 查询一个节点所有邻居的接口
查询的邻居中不应当包括“subject”，“object”和“predicate”这些特殊的边连出的点。

### 路径
/neighbours

### Input
请求报文结构

```json
{
    "entity": <String>
}
```

其中：
```
字段	含义
entity	查询实体的名称
```

例如
```json
{
    "entity": "发热"
}
```

### Output
返回报文结构
```json
{
    "neighbours": [<JSON>]
}
```

其中：
```
字段		含义
neighbours	查询节点的所有邻居信息列表，每个元素为“节点信息”JSON结构
```

节点信息JSON结构
```json
{
    "neighbourIsObject": <Boolean>,
    "predicate": <String>,
    "predicateID": <String>,
    "type": <String>,
    "name": <String>,
    "level": <int>
}
```
其中：
```
字段			含义
neighbourIsObject	邻居节点是否为关系的宾语
predicate		连接到邻居的关系名称
predicateID		连接到邻居的关系的ID
type			邻居实体类型
name			邻居实体名称
level			“导致”关系的置信等级，如果“predicate”为“导致”的时候该字段需要设置
```
例如
```json
{
    "neighbours": [
        {
            "neighbourIsObject": true,
            "predicate": "与",
            "predicateID": "05ad",
            "type": "症状",
            "name": "畏寒"
        },
        {
            "neighbourIsObject": false,
            "predicate": "导致",
            "predicateID": "3cb9",
            "type": "疾病",
            "name": "感冒",
            "level": 5
        },
        {
            "neighbourIsObject": false,
            "predicate": "修饰限定",
            "predicateID": "3c25",
            "type": "性质修饰语",
            "name": "持续性"
        }
    ]
}
```

## VI. 查询一个节点的上层嵌套结构的接口(未确定，先不做)
查询所有将当前节点作为子节点嵌套的节点结构。

### 路径
/upwardRecursion

### Input
```json
{
    "entity": <String>
}
```
其中：
```
字段	含义
entity	查询的实体名称
```
例如：
```json
{
    "entity": "发热"
}
```

### Output
```json
```