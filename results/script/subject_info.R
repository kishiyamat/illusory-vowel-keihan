library(tibble)

item_id2char <- function(item_id) {
  # see read_csv("../src/list/production_list.csv")
  case_when(
    item_id == 1 ~ "KUTouten",
    item_id == 2 ~ "aKUTenkou",
    item_id == 3 ~ "eSUPeranto",
    item_id == 4 ~ "SUPootsu",
    item_id == 5 ~ "ePUSon",
    item_id == 6 ~ "PUSan-meibutsu",
    item_id == 7 ~ "oTSUKai",
    item_id == 8 ~ "TSUKebarai"
  )
}

item_id2tone <- function(item_id) {
  # see read_csv("../src/list/production_list.csv")
  # tobe implemented
  # アクセント核なんかも考慮すべき？
  NULL
}

order_by_run_id <- function(df) {
  df %>%
    filter(task == "production" & type == "target") %>%
    mutate(
      run_id = as.integer(run_id),
      item_id = as.integer(item_id),
      present_order = as.integer(trial_index)
    ) %>%
    select(c(run_id, item_id, present_order))
}

extract_columns <- function(df, data_src) {
  if (!data_src %in% c("cw", "sone")) {
    stop("NotImplementedError")
  }
  cols <- c(age = NA)
  base_df <- df %>%
    filter(task != "production") %>%
    filter(trial_type == "survey-html-form") %>%
    select(c(run_id, response)) %>%
    mutate(
      run_id = as.integer(run_id),
      "key" = str_extract(response, "[a-z_]+"),
      "value" = response
    ) %>%
    select(-response) %>%
    pivot_wider(names_from = key, values_from = value) %>%
    mutate(span_tokyo = as.integer(str_extract(span_tokyo, "[0-9]+"))) %>%
    mutate(span_kinki = as.integer(str_extract(span_kinki, "[0-9]+"))) %>%
    mutate(subject_id = str_match(subject_id, ':"(.*?)"')[, 2]) %>%
    # パイロットのときのデータを除外
    filter(!subject_id %in% c("2000", "9001", "9002", "9003")) %>%
    mutate(subj_id = paste0(run_id, "_", subject_id)) %>%
    select(-c(subject_id)) %>%
    # age がないと下のcase_whenのsoneで失敗するので事前に追加
    add_column(!!!cols[!names(cols) %in% names(.)]) %>%
    mutate(age = case_when(
      data_src == "sone" ~ span_tokyo + span_kinki,
      data_src == "cw" ~ as.integer(str_extract(age, "[0-9]+"))
    )) %>%
    mutate(
      data_src = data_src,
      span_unknown = age - (span_tokyo + span_kinki)
    )
}

results_table <- function(annotated_df) {
  annotated_df %>%
    mutate(
      subj_id = substr(filename, 0, nchar(filename) - 2),
      item_id = as.integer(item_id),
      production_order = as.integer(order)
    ) %>%
    select(-c("filename", "order"))
}
