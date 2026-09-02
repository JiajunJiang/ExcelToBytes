# TODO

## 功能方向（可选）

- [ ] **嵌套组支持 repeated**
  - 现状：`src/interpreter.py` 中嵌套组目前只能生成单数 message 字段，不支持 repeated 结构组。
  - 目标：让整个嵌套组可以变成数组，例如 `Skills.ID` / `Skills.Level` 整组生成 `repeated Skills Skills = N;`，游戏配置里这个需求很常见。

- [ ] **批量导出**
  - 目标：支持一次传多个 xlsx 文件，或直接传一个目录批量导出。

- [ ] **枚举类型支持**
  - 目标：在表格类型声明中支持枚举（enum），生成对应的 proto enum 定义并校验单元格取值。

## 已完成

- [x] map 负数解析（2026-09-02）：`_parse_map_pair` 用正则在数字键上定位第一个不属于 key 的 `-`，`10--20`/`-5-10`/`-5--20` 均可正确切分。
- [x] 性能：表头只读一次（schema.py 缓存列元数据）、workbook 全程只打开一次、`nrows/ncols` 替代 `col_values` 物化、protoc 批量调用（python_out 一次 + 目标语言一次）、`archive` 移到所有 sheet 完成后执行一次。5000 行单表 0.75s→0.46s，6 sheet×2000 行 5.0s→0.64s，导出字节完全一致。
- [x] protoc 失败改为报错（subprocess 检查返回值），不再静默使用旧 `_pb2.py`。
