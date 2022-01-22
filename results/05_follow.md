Follow Up Survey
================

1.  無理に前提を置く必要はない。
    <https://github.com/kishiyamat/illusory-vowel-keihan/pull/118>
    をベースに資料を作成

単語とかはともかく、ピッチパターンが許容できるかを確認する

東京パターンか否かで考える

-   小豆(HHL-HLL-*LHH*)
-   カラス(*HLL*–LHH–LLH)
-   言葉(HHL–HLL–*LHH*)
-   ウサギ(*LHH*–LLH)

``` r
results <- read_csv("follow-up.csv") %>% 
  rename(
    input_id = "クラウドワークスのワーカー名",
    age = "現在の年齢"
    ) %>% 
  pivot_longer(
    cols = contains("H"),
    names_to = "stimuli",
    values_to = "evaluation"
  ) %>% 
  select(
    c(input_id, stimuli, evaluation)
  ) %>% 
  mutate(
    word =  gsub('[HL（）]', '', stimuli) ,
    word  = case_when(
      word=="ウサギ"~"usagi",
      word=="カラス"~"karasu",
      word=="言葉"~"kotoba",
      word=="小豆"~"azuki",
      TRUE ~ "other"),
    pattern = case_when(
      stimuli %in% c("小豆（LHH）", "カラス（HLL）", "言葉（LHH）", "ウサギ（LHH）") ~ "tokyo",
      TRUE ~ "other"),
    eval_int = case_when(
      evaluation=="よく聞く"~3,
      evaluation=="時々聞く"~2,
      evaluation=="あまり聞いたことがない"~1,
      evaluation=="全く聞いたことがない"~0
    )
  ) %>% 
  group_by(input_id, pattern, word) %>% 
  # 最大値を取れば外れ値などは関係ない
  # 平均は非東京パターンで割れたとき（0と3など）1.5などになってしまう。
  summarise(eval_by_pattern = max(eval_int)) %>% ungroup
```

    ## 
    ## ─ Column specification ────────────────────────────
    ## cols(
    ##   .default = col_character(),
    ##   現在の年齢 = col_double()
    ## )
    ## ℹ Use `spec()` for the full column specifications.

    ## `summarise()` regrouping output by 'input_id', 'pattern' (override with `.groups` argument)

``` r
results
```

    ## # A tibble: 256 x 4
    ##    input_id   pattern word   eval_by_pattern
    ##    <chr>      <chr>   <chr>            <dbl>
    ##  1 1takuya1   other   azuki                0
    ##  2 1takuya1   other   karasu               1
    ##  3 1takuya1   other   kotoba               0
    ##  4 1takuya1   other   usagi                0
    ##  5 1takuya1   tokyo   azuki                3
    ##  6 1takuya1   tokyo   karasu               2
    ##  7 1takuya1   tokyo   kotoba               3
    ##  8 1takuya1   tokyo   usagi                2
    ##  9 bambooblue other   azuki                3
    ## 10 bambooblue other   karasu               1
    ## # … with 246 more rows

``` r
item_list <- read_csv("../src/list/axb_list.csv") %>%
  select(c(item_id, type, condition, correct, item_a, item_x, item_b, c1, c2))
```

    ## 
    ## ─ Column specification ────────────────────────────
    ## cols(
    ##   .default = col_character(),
    ##   item_id = col_double(),
    ##   pair = col_double(),
    ##   speaker_1 = col_double(),
    ##   speaker_2 = col_double(),
    ##   speaker_3 = col_double()
    ## )
    ## ℹ Use `spec()` for the full column specifications.

``` r
subject_info_sone <- read_csv("csv/illusory-vowel-keihan.csv") %>%
  extract_columns(data_src = "sone")
```

    ## 
    ## ─ Column specification ────────────────────────────
    ## cols(
    ##   .default = col_character(),
    ##   run_id = col_double(),
    ##   condition = col_double(),
    ##   trial_index = col_double(),
    ##   time_elapsed = col_double(),
    ##   recorded_at = col_datetime(format = ""),
    ##   platform_version = col_double()
    ## )
    ## ℹ Use `spec()` for the full column specifications.

    ## Warning: 1766 parsing failures.
    ##  row              col               expected  actual                            file
    ## 1769 platform_version no trailing characters 10_15_7 'csv/illusory-vowel-keihan.csv'
    ## 1770 platform_version no trailing characters 10_15_7 'csv/illusory-vowel-keihan.csv'
    ## 1771 platform_version no trailing characters 10_15_7 'csv/illusory-vowel-keihan.csv'
    ## 1772 platform_version no trailing characters 10_15_7 'csv/illusory-vowel-keihan.csv'
    ## 1773 platform_version no trailing characters 10_15_7 'csv/illusory-vowel-keihan.csv'
    ## .... ................ ...................... ....... ...............................
    ## See problems(...) for more details.

``` r
subject_info_cw <- read_csv("csv/illusory-vowel-keihan-cw.csv") %>%
  extract_columns(data_src = "cw")
```

    ## 
    ## ─ Column specification ────────────────────────────
    ## cols(
    ##   .default = col_character(),
    ##   run_id = col_double(),
    ##   condition = col_double(),
    ##   trial_index = col_double(),
    ##   time_elapsed = col_double(),
    ##   recorded_at = col_datetime(format = ""),
    ##   platform_version = col_double()
    ## )
    ## ℹ Use `spec()` for the full column specifications.

    ## Warning: 5319 parsing failures.
    ##  row              col               expected  actual                               file
    ## 5911 platform_version no trailing characters 10_15_7 'csv/illusory-vowel-keihan-cw.csv'
    ## 5912 platform_version no trailing characters 10_15_7 'csv/illusory-vowel-keihan-cw.csv'
    ## 5913 platform_version no trailing characters 10_15_7 'csv/illusory-vowel-keihan-cw.csv'
    ## 5914 platform_version no trailing characters 10_15_7 'csv/illusory-vowel-keihan-cw.csv'
    ## 5915 platform_version no trailing characters 10_15_7 'csv/illusory-vowel-keihan-cw.csv'
    ## .... ................ ...................... ....... ..................................
    ## See problems(...) for more details.

``` r
# ここの input_id で合わせればいい
subject_info <- rbind(subject_info_sone, subject_info_cw) %>% 
  mutate(
    span_tokyo_span_kinki = span_tokyo - span_kinki,
    tokyo_kinki_ratio = (span_tokyo - span_kinki) / age
  )
```

``` r
follow_list = results$input_id %>% unique
# ↑に存在するが↓に存在しないパターンがよろしくない。
original_list = subject_info %>% filter(data_src=="cw") %>% select(input_id) %>% unlist %>% unique
# これらが問題
# 28しかない。4件落ちている。年齢から推定する(?)
`%notin%` <- Negate(`%in%`)
follow_list[follow_list %notin% original_list]
```

    ## [1] "Edifice"      "hanahanasuki" "ryou7727"     "wanko20"

``` r
# head(subject_info)
merged_results = results %>% merge(subject_info)
head(merged_results)
```

    ##   input_id pattern   word eval_by_pattern run_id span_tokyo span_kinki
    ## 1 1takuya1   tokyo  usagi               2    211          7          9
    ## 2 1takuya1   tokyo kotoba               3    211          7          9
    ## 3 1takuya1   other  usagi               0    211          7          9
    ## 4 1takuya1   tokyo  azuki               3    211          7          9
    ## 5 1takuya1   other karasu               1    211          7          9
    ## 6 1takuya1   other kotoba               0    211          7          9
    ##        subj_id age data_src span_unknown span_tokyo_span_kinki
    ## 1 211_1takuya1  32       cw           16                    -2
    ## 2 211_1takuya1  32       cw           16                    -2
    ## 3 211_1takuya1  32       cw           16                    -2
    ## 4 211_1takuya1  32       cw           16                    -2
    ## 5 211_1takuya1  32       cw           16                    -2
    ## 6 211_1takuya1  32       cw           16                    -2
    ##   tokyo_kinki_ratio
    ## 1           -0.0625
    ## 2           -0.0625
    ## 3           -0.0625
    ## 4           -0.0625
    ## 5           -0.0625
    ## 6           -0.0625

``` r
# -1から1の値を取る(まぁ0--4に分割、とかでいいか。)
merged_results %>% 
  ggplot() +
  facet_grid(pattern ~ word) +
  geom_violin(aes(
    x = factor(range01(tokyo_kinki_ratio), 4),
    y = eval_by_pattern,
    color = pattern,
    fill = pattern
  ))
```

![](05_follow_files/figure-gfm/unnamed-chunk-5-1.png)<!-- -->

東京居住歴が長くて東京以外のパターンを聞いたことがある人はいないが、
東京居住歴が短くて東京のパターンを聞いたことのある人はいる。

``` r
library(lmerTest)
```

    ## Loading required package: lme4

    ## Loading required package: Matrix

    ## 
    ## Attaching package: 'Matrix'

    ## The following objects are masked from 'package:tidyr':
    ## 
    ##     expand, pack, unpack

    ## 
    ## Attaching package: 'lmerTest'

    ## The following object is masked from 'package:lme4':
    ## 
    ##     lmer

    ## The following object is masked from 'package:stats':
    ## 
    ##     step

``` r
model <- lmer(
  eval_by_pattern ~
  pattern * tokyo_kinki_ratio + (1 | input_id) + (1 | word),
  data = merged_results)
```

``` r
summary(model)
```

    ## Linear mixed model fit by REML. t-tests use Satterthwaite's method [
    ## lmerModLmerTest]
    ## Formula: eval_by_pattern ~ pattern * tokyo_kinki_ratio + (1 | input_id) +  
    ##     (1 | word)
    ##    Data: merged_results
    ## 
    ## REML criterion at convergence: 544.5
    ## 
    ## Scaled residuals: 
    ##     Min      1Q  Median      3Q     Max 
    ## -2.7521 -0.6727  0.1743  0.6591  2.6071 
    ## 
    ## Random effects:
    ##  Groups   Name        Variance Std.Dev.
    ##  input_id (Intercept) 0.12559  0.3544  
    ##  word     (Intercept) 0.04389  0.2095  
    ##  Residual             0.55420  0.7444  
    ## Number of obs: 224, groups:  input_id, 28; word, 4
    ## 
    ## Fixed effects:
    ##                                 Estimate Std. Error        df t value Pr(>|t|)
    ## (Intercept)                      1.25150    0.14314   6.75442   8.743 6.34e-05
    ## patterntokyo                     1.10064    0.09993 190.99997  11.014  < 2e-16
    ## tokyo_kinki_ratio               -0.36811    0.11999  46.96440  -3.068  0.00358
    ## patterntokyo:tokyo_kinki_ratio   0.78165    0.12290 190.99997   6.360 1.46e-09
    ##                                   
    ## (Intercept)                    ***
    ## patterntokyo                   ***
    ## tokyo_kinki_ratio              ** 
    ## patterntokyo:tokyo_kinki_ratio ***
    ## ---
    ## Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1
    ## 
    ## Correlation of Fixed Effects:
    ##             (Intr) pttrnt tky_k_
    ## patterntoky -0.349              
    ## toky_knk_rt -0.064  0.048       
    ## pttrntky:__  0.033 -0.095 -0.512
