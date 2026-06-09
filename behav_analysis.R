library(tidyverse)
library(ggsignif)
theme_set(theme_minimal())
source("data_dir.R")

# PN
d <- read.csv2(
  data_dir,
  sep = ","
)

d$stim_congruence <- ifelse(d$stim_congruence == "True", TRUE, FALSE)
d$rt <- as.numeric(d$rt)
d <- d %>%
  mutate(correct_response = correct_response == "True")

# summarise mean RT and accuracy by condition and congruence
# filtering to correct trials only for RT
summary_df <- d %>%
  group_by(condition, stim_congruence) %>%
  summarise(
    mean_rt = mean(rt[correct_response], na.rm = TRUE),
    accuracy = mean(correct_response, na.rm = TRUE),
    n = n(),
    .groups = "drop"
  ) %>%
  mutate(congruence_label = ifelse(stim_congruence, "congruent", "incongruent"))

print(summary_df)

# calculate interference effect (incongruent - congruent RT) per condition
interference <- summary_df %>%
  select(condition, congruence_label, mean_rt) %>%
  pivot_wider(names_from = congruence_label, values_from = mean_rt) %>%
  mutate(interference_effect = incongruent - congruent)

print(interference) # faces win

# models
model_interact <- lm(
  rt ~ condition * stim_congruence,
  data = d %>% filter(correct_response)
)

summary(model_interact)

model_main <- lm(
  rt ~ condition + stim_congruence,
  data = d %>% filter(correct_response)
)

summary(model_main)


#model only face
df_face <- d %>% filter(condition == 'face')

model_face <- lm(
  rt ~ stim_congruence,
  data = df_face %>% filter(correct_response)
)

summary(model_face)

#model only word
df_word <- d %>% filter(condition == 'word')

model_word <- lm(
  rt ~ stim_congruence,
  data = df_word %>% filter(correct_response)
)

summary(model_word)

# plotting
n_correct <- d |>
  filter(correct_response) |> 
  count()

d |>
  filter(correct_response) |>
  mutate(congruence_label = ifelse(stim_congruence, "Congruent", "Incongruent")) |>
  ggplot(aes(x = congruence_label, y = rt, fill = congruence_label, color = congruence_label)) +
  geom_violin(linewidth = 0.5, alpha = 0.3) +
  geom_jitter(size = 0.9, alpha = 0.4, shape = 16, width = 0.15) +
  geom_signif(
    comparisons = list(c("Congruent", "Incongruent")),
    test = "t.test",
    map_signif_level = TRUE,  # shows *, **, *** instead of p-value
    color = "black",
    tip_length = 0.02
  ) +
  facet_wrap(~ condition) +
  scale_fill_manual(values = c("Congruent" = "#3E1C00", "Incongruent" = "#FF8C00")) +
  scale_color_manual(values = c("Congruent" = "#3E1C00", "Incongruent" = "#FF8C00")) +
  labs(x = NULL, y = "RT (s)", title = "RTs across task and congruency",
       caption = paste0("Note: Correct trials only (", n_correct, ")")) +
  theme(legend.position = "none")
