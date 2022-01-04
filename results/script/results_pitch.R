range01 <- function(x){(x-min(x))/(max(x)-min(x))}
factor = function(x, res) {as.factor(as.integer(floor(x*res)))}
# 補足データ
item_list <- "../src/list/axb_list.csv" %>%
  read_csv() %>%
  select(c(item_id, type, correct, item_a, item_x, item_b, pitch_a, pitch_x, pitch_b))
# devoicing_by_subj.csv は 00_devoicing.Rmdで作成
devoicing_annotation_subj <- read_csv("devoicing_by_subj.csv") # 被験者(data_src, run_id)ごとアノテーション

# 実験データ
tone_sone <- read_csv("csv/illusory-vowel-keihan.csv") %>%
  filter(task == "axb") %>%
  select(c(run_id, item_id, is_correct, rt, trial_index)) %>%
  mutate(data_src = "sone")
tone_cw <- read_csv("csv/illusory-vowel-keihan-cw.csv") %>%
  filter(task == "axb") %>%
  select(c(run_id, item_id, is_correct, rt, trial_index)) %>%
  mutate(data_src = "cw")

# 統合と列生成
results_pitch <- rbind(tone_sone, tone_cw) %>%
  left_join(devoicing_annotation_subj, by = c("run_id", "data_src")) %>%
  merge(item_list, on = "item_id") %>%
  filter(type != "target") %>%
  # toneの実験は "target" ではない
  mutate(
    pitch_from = case_when(
      correct == "a" ~ pitch_a, # 提示されたピッチ(e.g. H_L)
      correct == "b" ~ pitch_b
    ),
    pitch_to = case_when(
      correct == "a" ~ pitch_b, # 反対が母音あり版(e.g. HHL)
      correct == "b" ~ pitch_a
    ),
    phoneme = as.factor(str_sub(item_x, 1, -nchar(pitch_x) - 1))
  ) %>%
  mutate(pitch_type = case_when(
    pitch_to %in% c("-HL", "-HLL", "-LHH") ~ "Tokyo",
    pitch_to %in% c("-LL", "-HHL", "-LLH") ~ "Kinki"
  )) %>%
  filter(pitch_to %in% c("-HLL", "-LHH", "-HHL", "-LLH")) %>%
  drop_na() %>%
  mutate(
    is_correct = as.logical(is_correct),
    rt = as.numeric(rt),
    voiced = as.numeric(voiced),
    devoiced = as.numeric(devoiced)
  )