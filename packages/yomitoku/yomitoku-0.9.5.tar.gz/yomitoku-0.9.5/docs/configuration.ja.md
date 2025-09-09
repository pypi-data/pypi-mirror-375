# Configuration

各モジュールに対して、設定可能なパラメータについて説明します。

## Text Detector

### 入力画像サイズに関する設定

```yaml
data:
  # 画像の短辺ピクセル数が設定した数値を下回る場合にここで設定した画像のピクセル数に以上になるように画像を拡大します。
  shortest_size: int 

  #画像の長辺ピクセル数が設定した数値を上回る場合にここで設定した画像のピクセル数以下になるように画像を縮小します。
  limit_size: int 
```

### 後処理

```yaml
post_process:
  #検出した領域の辺の大きいさが設定した数値を下回る場合に領域を除去します。
  min_size: int 

  #モデルの予測スコアに対する閾値で、予測スコアが設定した閾値を下回るピクセルを背景領域として扱います。
  thresh: float 

  #領域内の予測の平均スコアに対する閾値で、閾値を下回る領域を除外する
  box_thresh: float 

  #検出可能なテキスト領域数の上限
  max_candidates: int 

  #テキスト領域のマージン領域の大きさを設定するためのパラメータ。大きいほど、テキスト領域のマージンを大きくし、余白を持たせた検出が可能になり、小さいほどタイトな検出になる。
  unclip_ratio: int 
```

### 可視化設定

```yaml
visualize:
  #検出領域のバウンディングボックスの色の設定
  color: [B, G, R] 

  #モデルの予測ヒートマップを可視化、描画するか
  heatmap: boolean 
```

## Text Recognizer

### 文字列長

```yaml
#予測可能な最大文字列長
max_label_length: int
```

### 入力画像

```yaml
data:
   #バッチ処理に用いる画像数
  batch_size: int
```

### 可視化設定

```yaml
visualize:
  # 予測結果文字列の可視化に用いるフォントのパス
  font: str 

  # 予測結果文字列の可視化に用いるフォントの色
  color: [BGR] 

  # 予測結果文字列のフォントの大きさ
  font_size: int
```

## Layout_parser

### 予測スコアに対する閾値

```yaml
#モデルの予測スコアに対する閾値で、予測スコアが設定した閾値を領域を除外します。
thresh_score: float 
```

## Table Structure Recognizer

### 予測スコアに対する閾値

```yaml
#モデルの予測スコアに対する閾値で、予測スコアが設定した閾値を領域を除外します。
thresh_score: float 
```
