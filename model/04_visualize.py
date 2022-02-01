# 1. Model
# 1. Feature
# 1. Inference

# %%
print(model.le.classes_)
print(plt.imshow(model.acoustic.likelihood(
    model.acoustic.imputer.transform(X_flatten))))
plt.show()
print(model.tmat)
print(model.startprob)
print(plt.imshow(model.duration))
plt.show()


def draw_features(self):
    label_name = 'semitone' if self.use_duration else "pitch"
    color_name = "rle_label" if self.use_duration else "label"
    df = pd.DataFrame({label_name: self._X_imputed[:, 0],
                       color_name: self.le.inverse_transform(self._y),
                       'silent': self._X[:, 1]})
    p = (ggplot(df, aes(x=label_name, color=color_name, fill=color_name))
         + facet_grid(f"{color_name} ~ silent")
         + geom_histogram()
         + labs(x=label_name, y="count")
         + scale_y_log10()
         )
    return p


def draw_duration(self):
    p = (ggplot(self.dur_df, aes(x='duration', color="label", fill="label"))
         + facet_grid(". ~ label")
         + geom_histogram(bins=20)
         + labs(x='duration', y='count')
         )
    return p
