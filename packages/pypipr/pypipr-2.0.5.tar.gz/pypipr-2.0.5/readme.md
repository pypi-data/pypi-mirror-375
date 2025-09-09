
# ComparePerformance
Menjalankan seluruh method dalam class,
Kemudian membandingkan waktu yg diperlukan.
Nilai 100 berarti yang tercepat.

example : 
```python
def test():
    import pprint

    class ExampleComparePerformance(ComparePerformance):
        # number = 1
        z = 10

        def a(self):
            return (x for x in range(self.z))

        def b(self):
            return tuple(x for x in range(self.z))

        def c(self):
            return [x for x in range(self.z)]

        def d(self):
            return list(x for x in range(self.z))

    pprint.pprint(ExampleComparePerformance().compare_result())
    print(ExampleComparePerformance().compare_performance())
    print(ExampleComparePerformance().compare_performance())
    print(ExampleComparePerformance().compare_performance())
    print(ExampleComparePerformance().compare_performance())
    print(ExampleComparePerformance().compare_performance())

```

result : 
```shell
{'a': <generator object test.<locals>.ExampleComparePerformance.a.<locals>.<genexpr> at 0x793f0fa200>,
 'b': (0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
 'c': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
 'd': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]}
{'a': 165, 'b': 188, 'c': 100, 'd': 161}
{'a': 119, 'b': 155, 'c': 100, 'd': 165}
{'a': 126, 'b': 168, 'c': 100, 'd': 185}
{'a': 126, 'b': 167, 'c': 99, 'd': 181}
{'a': 128, 'b': 170, 'c': 99, 'd': 185}

```


# LINUX
bool(x) -> bool

Returns True when the argument x is true, False otherwise.
The builtins True and False are the only two instances of the class bool.
The class bool is a subclass of the class int, and cannot be subclassed.

example : 
```python
def test():
    print(LINUX)

```

result : 
```shell
True

```


# batch_calculate
Analisa perhitungan massal.
Bisa digunakan untuk mencari alternatif terendah/tertinggi/dsb.

example : 
```python
def test():
    import pprint
    print(batch_calculate("{1 10} m ** {1 3}"))
    pprint.pprint(list(batch_calculate("{1 10} m ** {1 3}")))

```

result : 
```shell
<generator object batch_calculate at 0x793f21b300>
[('1 m ** 1', <Quantity(1, 'meter')>),
 ('1 m ** 2', <Quantity(1, 'meter ** 2')>),
 ('1 m ** 3', <Quantity(1, 'meter ** 3')>),
 ('2 m ** 1', <Quantity(2, 'meter')>),
 ('2 m ** 2', <Quantity(2, 'meter ** 2')>),
 ('2 m ** 3', <Quantity(2, 'meter ** 3')>),
 ('3 m ** 1', <Quantity(3, 'meter')>),
 ('3 m ** 2', <Quantity(3, 'meter ** 2')>),
 ('3 m ** 3', <Quantity(3, 'meter ** 3')>),
 ('4 m ** 1', <Quantity(4, 'meter')>),
 ('4 m ** 2', <Quantity(4, 'meter ** 2')>),
 ('4 m ** 3', <Quantity(4, 'meter ** 3')>),
 ('5 m ** 1', <Quantity(5, 'meter')>),
 ('5 m ** 2', <Quantity(5, 'meter ** 2')>),
 ('5 m ** 3', <Quantity(5, 'meter ** 3')>),
 ('6 m ** 1', <Quantity(6, 'meter')>),
 ('6 m ** 2', <Quantity(6, 'meter ** 2')>),
 ('6 m ** 3', <Quantity(6, 'meter ** 3')>),
 ('7 m ** 1', <Quantity(7, 'meter')>),
 ('7 m ** 2', <Quantity(7, 'meter ** 2')>),
 ('7 m ** 3', <Quantity(7, 'meter ** 3')>),
 ('8 m ** 1', <Quantity(8, 'meter')>),
 ('8 m ** 2', <Quantity(8, 'meter ** 2')>),
 ('8 m ** 3', <Quantity(8, 'meter ** 3')>),
 ('9 m ** 1', <Quantity(9, 'meter')>),
 ('9 m ** 2', <Quantity(9, 'meter ** 2')>),
 ('9 m ** 3', <Quantity(9, 'meter ** 3')>),
 ('10 m ** 1', <Quantity(10, 'meter')>),
 ('10 m ** 2', <Quantity(10, 'meter ** 2')>),
 ('10 m ** 3', <Quantity(10, 'meter ** 3')>)]

```


# batchmaker
Alat Bantu untuk membuat teks yang berulang.
Gunakan `{[start][separator][finish]([separator][step])}`.
```
[start] dan [finish]    -> bisa berupa huruf maupun angka
([separator][step])     -> bersifat optional
[separator]             -> selain huruf dan angka
[step]                  -> berupa angka positif
```

example : 
```python
def test():
    import pprint
    pattern = "Urutan {1/6/3} dan {10:9} dan {j k} dan {Z - A - 15} saja."
    pprint.pprint(list(batchmaker(pattern)))

```

result : 
```shell
['Urutan 1 dan 10 dan j dan Z saja.',
 'Urutan 1 dan 10 dan j dan K saja.',
 'Urutan 1 dan 10 dan j dan  saja.',
 'Urutan 1 dan 10 dan k dan Z saja.',
 'Urutan 1 dan 10 dan k dan K saja.',
 'Urutan 1 dan 10 dan k dan  saja.',
 'Urutan 1 dan 9 dan j dan Z saja.',
 'Urutan 1 dan 9 dan j dan K saja.',
 'Urutan 1 dan 9 dan j dan  saja.',
 'Urutan 1 dan 9 dan k dan Z saja.',
 'Urutan 1 dan 9 dan k dan K saja.',
 'Urutan 1 dan 9 dan k dan  saja.',
 'Urutan 4 dan 10 dan j dan Z saja.',
 'Urutan 4 dan 10 dan j dan K saja.',
 'Urutan 4 dan 10 dan j dan  saja.',
 'Urutan 4 dan 10 dan k dan Z saja.',
 'Urutan 4 dan 10 dan k dan K saja.',
 'Urutan 4 dan 10 dan k dan  saja.',
 'Urutan 4 dan 9 dan j dan Z saja.',
 'Urutan 4 dan 9 dan j dan K saja.',
 'Urutan 4 dan 9 dan j dan  saja.',
 'Urutan 4 dan 9 dan k dan Z saja.',
 'Urutan 4 dan 9 dan k dan K saja.',
 'Urutan 4 dan 9 dan k dan  saja.',
 'Urutan 7 dan 10 dan j dan Z saja.',
 'Urutan 7 dan 10 dan j dan K saja.',
 'Urutan 7 dan 10 dan j dan  saja.',
 'Urutan 7 dan 10 dan k dan Z saja.',
 'Urutan 7 dan 10 dan k dan K saja.',
 'Urutan 7 dan 10 dan k dan  saja.',
 'Urutan 7 dan 9 dan j dan Z saja.',
 'Urutan 7 dan 9 dan j dan K saja.',
 'Urutan 7 dan 9 dan j dan  saja.',
 'Urutan 7 dan 9 dan k dan Z saja.',
 'Urutan 7 dan 9 dan k dan K saja.',
 'Urutan 7 dan 9 dan k dan  saja.']

```


# random_bool
Menghasilkan nilai random True atau False.
Fungsi ini merupakan fungsi tercepat untuk mendapatkan random bool.
Fungsi ini sangat cepat, tetapi pemanggilan fungsi ini membutuhkan
overhead yg besar.

example : 
```python
def test():
    print(random_bool())

```

result : 
```shell
False

```
