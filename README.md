## Nepal Sambat Calendar (Python)

Based on: [NSAlgorithm by Spiral Logics](https://nsapi.spiralogics.net/nsalgorithm.pdf)


### About
This is a simple python script that uses [skyfield](https://pypi.org/project/skyfield/) to convert python datetime object into Nepal Sambat Date. 

### Nepal Sambat
Nepal Sambat is a lunisolar calendar in use in
Nepal since 879 AD.

```python
pip install -r requirements.txt
```
```bash
python nepal_sambat.py 2024-02-02

2027/03/12      चिल्लाथ्व, चतुथी (4)       1147
```
#### To Dos
- handle for leap month
- handle for skip month
- proper output string
- use devanagiri integers for output
- refactor