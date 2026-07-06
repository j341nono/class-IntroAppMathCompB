# Homework 3: IIT のパリティ例

このフォルダには、Integrated Information Theory（IIT）の課題用に作成した、実行可能な Python プログラムを置いています。

## 例の概要

このプログラムでは IIT の例として、3 つの二値ユニットの次状態が次のパリティ規則を満たす場合を考えます。

```text
C = A xor B
```

この例の面白い点は、1 つずつのユニットを見るとそれぞれ公平なコインのように見えることです。さらに、2 つのユニットの組だけを見ても強い制約は見えません。しかし、3 つ全体を見ると、可能な未来状態の半分が禁止されています。

つまり、部分だけでは見えない関係が、全体としては存在しています。簡略化した IIT 的な計算では、システムを分割するとこの全体的な関係が失われます。

スクリプトでは、次の量をいくつかの分割について計算し、図として表示します。

```text
phi = D_KL(whole effect repertoire || partitioned effect repertoire)
```

![IIT parity example plot](iit_parity_example.png)

## ファイル

- `environment.yml`: プログラムを実行するための Conda 環境ファイルです。
- `iit_parity_example.py`: プロットを作成する実行可能な Python スクリプトです。
- `iit_parity_example.png`: スクリプトを実行すると生成される図です。

## 実行方法

以下のコマンドを `homework3/` をカレントディレクトリとした状態で実行します。

```bash
conda env create -f environment.yml
conda activate iit-homework3
./iit_parity_example.py
```

実行すると、プロット画面が表示され、同時に `iit_parity_example.png` が保存されます。

## 結果の見方

オレンジ色の棒は、システムを分割した後の分布を表しています。この場合、8 つの未来状態がすべて同じ確率になります。

緑色の棒は、全体として見たときの effect repertoire を表しています。こちらでは、XOR のパリティ関係を満たす 4 つの状態だけが可能です。

分割されたシステムではパリティ関係を表せないため、KL divergence は正の値になります。この toy model では、最小の分割でも `1.00 bit` の情報が失われるので、簡略化した統合情報は次のようになります。

```text
phi = 1.00 bit
```

