# Analiza wydźwięku depesz giełdowych za pomocą modelu typu BERT

Celem projektu jest wykorzystanie polskiego modelu typu BERT (np. Herbert albo Polbert) do oceny wydźwięku (negatywny/neutralny/pozytywny) depesz na polskiej Giełdzie Papierów Wartościowych.

## Zawartość projektu
- Projekt zawiera skrypty do trenowania oraz ewaluacji modeli opartych na BERT (Herbert) do oceny wydźwięku.
- Przygotowane zbiory oraz kod pozwalają na uruchomienie trenowania modelu na danych pochodzących ze zbioru [Klej](https://klejbenchmark.com/tasks/#polemo2.0-in)
jak i [danych finansowych](data/annotated) składających się z pobranych z [raportów spółek ESPI](http://infostrefa.com/infostrefa/pl/raporty/espi/biezace,0,0,0,1) depesz giełdowych oraz kursów akcji z platformy [quandl](https://www.quandl.com/data/WSE-Warsaw-Stock-Exchange-GPW).
- Wygenerowanie powyższych było częścią projektu.
---
## Przygotowanie środowiska
1. Przed uruchomieniem projektu, należy utworzyć środowisko wirualne za pomocą anacondy.
2. Następnie będąc już w aktywowanym środowisku należy uruchomić polecenie:
```
conda install --yes --file requirements.txt
```

## Jak użyć?
Dwa najważniejsze dla użytkownika skrypty znajdują się w folderze [src/scripts/models](src/scripts/models/).

- Uruchomienie procesu trenowania modelu odbywa się za pomocą polecenia:
```
python -m src.scripts.models.train_model -o sciezka/do/zapisu/modelu --train_dataset DATASET_NAME
```

gdzie DATASET_NAME jest jedną z wartości: "klej_in", "financial_mixed", "financial".
Dodatkowo można sterować:
- liczbą epok za pomocą flagi ```--epochs```, 
- rozmiarem batcha treningowego za pomocą flagi ```--batch_size```, 
- rozmiarem batcha ewaluacyjnego za pomocą flagi ```--eval_batch_size```.  
---
- Uruchomienie procesu ewaluacji wytrenowanego modelu za pomocą polecenia:
```
python -m src.scripts.models.evaluate_model -i sciezka/do/zapisanego/modelu --test_dataset DATASET_NAME
```
gdzie DATASET_NAME jest jedną z wartości: "klej_in", "klej_out", "financial_mixed", "financial".
Dodatkowo można sterować:
- rozmiarem batcha ewaluacyjnego za pomocą flagi ```--eval_batch```.

---
Zaleca się uruchomienie projektu na środowisku z dostępem do GPU oraz CUDA, np. [google colab](https://colab.research.google.com/).
