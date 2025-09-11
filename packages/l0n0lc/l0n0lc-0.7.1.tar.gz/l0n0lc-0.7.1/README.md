# 将python函数翻译为c++函数并运行

## hello_world.py
```python
import l0n0lc as lc
import math


@lc.映射函数(math.ceil, ['<cmath>'])
def cpp_ceil(v):
    return f'std::ceil({lc.toCString(v)});'


@lc.映射函数(print, ['<iostream>'])
def cpp_cout(*args):
    code = f'std::cout'
    for arg in args:
        code += f'<< {lc.toCString(arg)} << " "'
    code += '<< std::endl;'
    return code


@lc.jit(每次运行都重新编译=True)
def test_add(a: int, b: int) -> int:
    if a > 1:
        return a + b
    for i in range(1, 10, 2):
        a += i
    for i in [1, 2, 3]:
        a += i
    a = math.ceil(12.5)
    cc = {'a': 1, 'b': 2}
    cc['c'] = 3
    print('输出map:')
    for ii in cc:
        print(ii.first, ii.second) # type: ignore
    aa = [1, 3, 2]
    aa[0] = 134
    print('输出list:')
    for i in range(3):
        print(i, aa[i])
    print('Hello World', a, b)
    return a + b + 1


print('结果:', test_add(1, 3))
```
## 执行hello_world.py
```bash
$ python hello_world.py
输出map: 
c 3 
a 1 
b 2 
输出list: 
0 134 
1 3 
2 2 
Hello World 13 3 
结果: 17
```
## 查看生成的c++代码文件
```bash
$ ls -al l0n0lcoutput
total 44
drwxr-xr-x  2 root root  4096 Sep 11 01:38 .
drwxrwxrwx 12 1000 1000  4096 Sep 10 02:36 ..
-rw-r--r--  1 root root   599 Sep 11 01:38 test_add_@402bbf73254216d8.cpp
-rw-r--r--  1 root root   150 Sep 11 01:38 test_add_@402bbf73254216d8.h
-rwxr-xr-x  1 root root 25264 Sep 11 01:38 test_add_@402bbf73254216d8.so
```

## test_add_@402bbf73254216d8.h

```c++
#include <cmath>
#include <cstdint>
#include <iostream>
#include <string>
#include <unordered_map>
extern "C" int64_t test_add (int64_t a, int64_t b);
```

## test_add_@402bbf73254216d8.cpp
```c++
#include "test_add_@141921ba1aaa0352.h"
extern "C" int64_t test_add (int64_t a, int64_t b)
{
  if ((a > 1))
  {
    return a + b;
  }

  for (int64_t i = 1; i < 10; i += 2)
  {
    a = a + i;
  }

  for (auto i : {1,2,3})
  {
    a = a + i;
  }

  a = std::ceil(12.5);;
  std::unordered_map<std::string, int64_t> cc = {{ u8"a", 1 },{ u8"b", 2 }};
  cc[u8"c"] = 3;
  std::cout<< u8"输出map:" << " "<< std::endl;
  for (auto ii : cc)
  {
    std::cout<< ii.first << " "<< ii.second << " "<< std::endl;
  }

  int64_t aa[] = {1,3,2};
  aa[0] = 134;
  std::cout<< u8"输出list:" << " "<< std::endl;
  for (int64_t i = 0; i < 3; ++i)
  {
    std::cout<< i << " "<< aa[i] << " "<< std::endl;
  }

  std::cout<< u8"Hello World" << " "<< a << " "<< b << " "<< std::endl;
  return a + b + 1;
}
```