library(estimatr);
library(AER);
library("plyr")
library(dplyr)
library(stargazer)
library(tibble)
library(ggplot2)
library(dotwhisker)
library(broom)
library(dplyr)
library(reshape2)

setwd("~/dev/human_compactness/")
df <- as.data.frame(read.csv("./grouped_data.csv"))

df_09 <- as.data.frame(read.csv("./30_results/09_df.csv"))
df_13 <- as.data.frame(read.csv("./30_results/13_df.csv"))
df_16 <- as.data.frame(read.csv("./30_results/16_df.csv"))
df_22 <- as.data.frame(read.csv("./30_results/22_df.csv"))
df_23 <- as.data.frame(read.csv("./30_results/23_df.csv"))
df_24 <- as.data.frame(read.csv("./30_results/24_df.csv"))
df_33 <- as.data.frame(read.csv("./30_results/33_df.csv"))
df_44 <- as.data.frame(read.csv("./30_results/44_df.csv"))
df_49 <- as.data.frame(read.csv("./30_results/49_df.csv"))
df_55 <- as.data.frame(read.csv("./30_results/55_df.csv"))

b <- c(-Inf, 21, 23, Inf)
names <-c("Small", "Medium", "Large")

df_09$district_type <- cut(df_09$log_area, breaks=b, labels=names)
df_13$district_type <- cut(df_13$log_area, breaks=b, labels=names)
df_16$district_type <- cut(df_16$log_area, breaks=b, labels=names)
df_22$district_type <- cut(df_22$log_area, breaks=b, labels=names)
df_23$district_type <- cut(df_23$log_area, breaks=b, labels=names)
df_24$district_type <- cut(df_24$log_area, breaks=b, labels=names)
df_33$district_type <- cut(df_33$log_area, breaks=b, labels=names)
df_44$district_type <- cut(df_44$log_area, breaks=b, labels=names)
df_49$district_type <- cut(df_49$log_area, breaks=b, labels=names)
df_55$district_type <- cut(df_55$log_area, breaks=b, labels=names)

df_09$district_type <- cut(df_09$log_area, breaks=3, labels=names)
df_13$district_type <- cut(df_13$log_area, breaks=3, labels=names)
df_16$district_type <- cut(df_16$log_area, breaks=3, labels=names)
df_22$district_type <- cut(df_22$log_area, breaks=3, labels=names)
df_23$district_type <- cut(df_23$log_area, breaks=3, labels=names)
df_24$district_type <- cut(df_24$log_area, breaks=3, labels=names)
df_33$district_type <- cut(df_33$log_area, breaks=3, labels=names)
df_44$district_type <- cut(df_44$log_area, breaks=3, labels=names)
df_49$district_type <- cut(df_49$log_area, breaks=3, labels=names)
df_55$district_type <- cut(df_55$log_area, breaks=3, labels=names)

df_09$state <- "Connecticut"
df_13$state <- "Georgia"
df_16$state <- "Idaho"
df_22$state <- "Louisiana"
df_23$state <- "Maine"
df_24$state <- "Maryland"
df_33$state <- "New Hampshire"
df_44$state <- "Rhode Island"
df_49$state <- "Utah"
df_55$state <- "Wisconsin"

all_districts <- rbind(df_09, df_13, df_16, df_22, df_23, df_24, df_33, df_44, df_49, df_55)

ggplot(all_districts, aes(x=sd, fill=district_type, color=district_type)) +
  ggtitle("KDE plot of different districts and their spatial diversity")
  geom_density(alpha=0.5) +
  theme_minimal() +
  theme( 
    panel.grid.major = element_blank(),
    panel.grid.minor = element_blank(),
    axis.title.y = element_blank(),
  ) + facet_wrap(. ~state, scales="free")

# Run regressions (main result)

hc_reg <- lm(df$sd ~ df$hc + factor(df$state) - 1)
pp_reg <- lm(df$sd ~ df$pp + factor(df$state) - 1)
reock_reg <- lm(df$sd ~ df$reock + factor(df$state) - 1)
ch_reg <- lm(df$sd ~ df$ch + factor(df$state) - 1)

hc_1 <- tidy(hc_reg) %>% filter(!grepl('state*', term))
pp_1 <- tidy(pp_reg) %>% filter(!grepl('state*', term))
reock_1 <- tidy(reock_reg) %>% filter(!grepl('state*', term))
ch_1 <- tidy(ch_reg) %>% filter(!grepl('state*', term))

tidied <- rbind(hc_1, pp_1, reock_1, ch_1)

dwplot(tidied,
       vline = geom_vline(xintercept = 0, colour = "grey60", linetype = 2)) %>%
      relabel_predictors(c('df$ch' = "Convex Hull", 'df$hc' = 'Human Compactness', 
                           'df$pp' = "Polsby-Popper", 'df$reock' = "Reock")) +
      ggtitle("Coefficient estimates of OLS regressions") + 
      theme_classic(base_size=15) +
        xlab("Coefficient Estimate") +
    theme(plot.title = element_text(face="bold"), legend.position="none")

# stargazer(hc_reg, pp_reg, reock_reg, ch_reg,
#           title= "OLS Regression of spatial diversity on various compactness metrics",
#           keep=c("hc", "pp", "reock", "ch"),
#           covariate.labels=c("Human compactness", "Polsby-Popper", "Reock", "Convex Hull"),
#           dep.var.labels = "Spatial diversity"
#           )

# Next, run regressions for each threshold

hc_10 <- as.data.frame(read.csv("./top_plan_0.1_0.csv"))
pp_10 <- as.data.frame(read.csv("./top_plan_0.1_1.csv"))
reock_10 <- as.data.frame(read.csv("./top_plan_0.1_2.csv"))
ch_10 <- as.data.frame(read.csv("./top_plan_0.1_3.csv"))

hc_25 <- as.data.frame(read.csv("./top_plan_0.25_0.csv"))
pp_25 <- as.data.frame(read.csv("./top_plan_0.25_1.csv"))
reock_25 <- as.data.frame(read.csv("./top_plan_0.25_2.csv"))
ch_25 <- as.data.frame(read.csv("./top_plan_0.25_3.csv"))

hc_50 <- as.data.frame(read.csv("./top_plan_0.5_0.csv"))
pp_50 <- as.data.frame(read.csv("./top_plan_0.5_1.csv"))
reock_50 <- as.data.frame(read.csv("./top_plan_0.5_2.csv"))
ch_50 <- as.data.frame(read.csv("./top_plan_0.5_3.csv"))

hc_75 <- as.data.frame(read.csv("./top_plan_0.75_0.csv"))
pp_75 <- as.data.frame(read.csv("./top_plan_0.75_1.csv"))
reock_75 <- as.data.frame(read.csv("./top_plan_0.75_2.csv"))
ch_75 <- as.data.frame(read.csv("./top_plan_0.75_3.csv"))

hc_90 <- as.data.frame(read.csv("./top_plan_0.9_0.csv"))
pp_90 <- as.data.frame(read.csv("./top_plan_0.9_1.csv"))
reock_90 <- as.data.frame(read.csv("./top_plan_0.9_2.csv"))
ch_90 <- as.data.frame(read.csv("./top_plan_0.9_3.csv"))

hc_10_reg <- lm(sd ~ hc + factor(state) - 1, data=hc_10)
pp_10_reg <- lm(sd ~ pp + factor(state) - 1, data=pp_10)
reock_10_reg <- lm(sd ~ reock + factor(state) - 1, data=reock_10)
ch_10_reg <- lm(sd ~ ch + factor(state) - 1, data=ch_10)

hc_25_reg <- lm(sd ~ hc + factor(state) - 1, data=hc_25)
pp_25_reg <- lm(sd ~ pp + factor(state) - 1, data=pp_25)
reock_25_reg <- lm(sd ~ reock + factor(state) - 1, data=reock_25)
ch_25_reg <- lm(sd ~ ch + factor(state) - 1, data=ch_25)

hc_50_reg <- lm(sd ~ hc + factor(state) - 1, data=hc_50)
pp_50_reg <- lm(sd ~ pp + factor(state) - 1, data=pp_50)
reock_50_reg <- lm(sd ~ reock + factor(state) - 1, data=reock_50)
ch_50_reg <- lm(sd ~ ch + factor(state) - 1, data=ch_50)

hc_75_reg <- lm(sd ~ hc + factor(state) - 1, data=hc_75)
pp_75_reg <- lm(sd ~ pp + factor(state) - 1, data=pp_75)
reock_75_reg <- lm(sd ~ reock + factor(state) - 1, data=reock_75)
ch_75_reg <- lm(sd ~ ch + factor(state) - 1, data=ch_75)

hc_90_reg <- lm(sd ~ hc + factor(state) - 1, data=hc_90)
pp_90_reg <- lm(sd ~ pp + factor(state) - 1, data=pp_90)
reock_90_reg <- lm(sd ~ reock + factor(state) - 1, data=reock_90)
ch_90_reg <- lm(sd ~ ch + factor(state) - 1, data=ch_90)

hc10 <- tidy(hc_10_reg) %>% filter(!grepl('state*', term))
pp10 <- tidy(pp_10_reg) %>% filter(!grepl('state*', term))
re10 <- tidy(reock_10_reg) %>% filter(!grepl('state*', term))
ch10 <- tidy(ch_10_reg) %>% filter(!grepl('state*', term))

hc25 <- tidy(hc_25_reg) %>% filter(!grepl('state*', term))
pp25 <- tidy(pp_25_reg) %>% filter(!grepl('state*', term))
re25 <- tidy(reock_25_reg) %>% filter(!grepl('state*', term))
ch25 <- tidy(ch_25_reg) %>% filter(!grepl('state*', term))

hc50 <- tidy(hc_50_reg) %>% filter(!grepl('state*', term))
pp50 <- tidy(pp_50_reg) %>% filter(!grepl('state*', term))
re50 <- tidy(reock_50_reg) %>% filter(!grepl('state*', term))
ch50 <- tidy(ch_50_reg) %>% filter(!grepl('state*', term))

hc75 <- tidy(hc_75_reg) %>% filter(!grepl('state*', term))
pp75 <- tidy(pp_75_reg) %>% filter(!grepl('state*', term))
re75 <- tidy(reock_75_reg) %>% filter(!grepl('state*', term))
ch75 <- tidy(ch_75_reg) %>% filter(!grepl('state*', term))

hc90 <- tidy(hc_90_reg) %>% filter(!grepl('state*', term))
pp90 <- tidy(pp_90_reg) %>% filter(!grepl('state*', term))
re90 <- tidy(reock_90_reg) %>% filter(!grepl('state*', term))
ch90 <- tidy(ch_90_reg) %>% filter(!grepl('state*', term))


tidied_10 <- rbind(hc10, pp10, re10, ch10)
tidied_10$model <- "10th percentile"

tidied_25 <- rbind(hc25, pp25, re25, ch25)
tidied_25$model <- "25th percentile"

tidied_50 <- rbind(hc50, pp50, re50, ch50)
tidied_50$model <- "50th percentile"

tidied_75 <- rbind(hc25, pp25, re25, ch25)
tidied_75$model <- "75th percentile"

tidied_90 <- rbind(hc90, pp90, re90, ch90)
tidied_90$model <- "90th percentile"

hc_reg <- lm(sd ~ hc + factor(state) - 1, data =df)
pp_reg <- lm(sd ~ pp + factor(state) - 1, data=df)
reock_reg <- lm(sd ~ reock + factor(state) - 1, data=df)
ch_reg <- lm(sd ~ ch + factor(state) - 1, data=df)

hc_all <- tidy(hc_reg) %>% filter(!grepl('state*', term))
pp_all <- tidy(pp_reg) %>% filter(!grepl('state*', term))
reock_all <- tidy(reock_reg) %>% filter(!grepl('state*', term))
ch_all<- tidy(ch_reg) %>% filter(!grepl('state*', term))

tidied_0 <- rbind(hc_all, pp_all, reock_all, ch_all)
tidied_0$model <- "0th percentile (all)"

tidied_all <-rbind(tidied_10, tidied_25, tidied_50, tidied_75, tidied_90, tidied_0)

dwplot(tidied_all,
       vline = geom_vline(xintercept = 0, colour = "grey60", linetype = 2)) %>%
      relabel_predictors(c('ch' = "Convex Hull", 'hc' = 'Human Compactness', 
                           'pp' = "Polsby-Popper", 'reock' = "Reock")) +
      theme_classic(base_size=15) +
        xlab("Coefficient Estimate") +
    theme(plot.title = element_text(face="bold"))

# Run pairwise t-tests

df_hc <- as.data.frame(read.csv("./top_plan_0.csv"))
df_pp <- as.data.frame(read.csv("./top_plan_1.csv"))
df_reock <- as.data.frame(read.csv("./top_plan_2.csv"))
df_ch <- as.data.frame(read.csv("./top_plan_3.csv"))

tt0 <- tidy(t.test(df_hc$sd, df$sd))
tt1 <- tidy(t.test(df_pp$sd, df$sd))
tt2 <- tidy(t.test(df_reock$sd, df$sd))
tt3 <- tidy(t.test(df_ch$sd, df$sd))
tt4 <- tidy(t.test(df_hc$sd, df_pp$sd))
tt5 <- tidy(t.test(df_hc$sd, df_reock$sd))
tt6 <- tidy(t.test(df_hc$sd, df_ch$sd))
tt7 <- tidy(t.test(df_pp$sd, df_reock$sd))
tt8 <- tidy(t.test(df_pp$sd, df_ch$sd))
tt9 <- tidy(t.test(df_reock$sd, df_ch$sd))

tt0$term <- "Human Compactness vs All"
tt1$term <- "Polsby-Popper vs All"
tt2$term <- "Reock vs All"
tt3$term <- "Convex Hull vs All"
tt4$term <- "Human Compactness vs Polsby-Popper"
tt5$term <- "Human Compactness vs Reock"
tt6$term <- "Human Compactness vs Convex Hull"
tt7$term <- "Polsby-Popper vs Reock"
tt8$term <- "Polsby-Popper vs Convex Hull"
tt9$term <- "Reock vs Convex Hull"

tt0$model <- "blue"
tt1$model <- "red"
tt2$model <- "red"
tt3$model <- "red"
tt4$model <- "blue"
tt5$model <- "blue"
tt6$model <- "blue"
tt7$model <- "red"
tt8$model <- "red"
tt9$model <- "red"

all_ttests <- rbind(tt0, tt1, tt2, tt3)
pairwise_ttests <- rbind(tt0, tt1, tt2, tt3, tt4, tt5, tt6, tt7, tt8, tt9)

dwplot(pairwise_ttests,
       vline = geom_vline(xintercept = 0, colour = "grey60", linetype = 2)) +
  ggtitle("Difference in spatial diversity between top plans") + 
  theme_classic(base_size=15) +
  theme(
    plot.title = element_text(face="bold"), legend.position="none"
    )


# Try and plot a nice correlation matrix

# Get lower triangle of the correlation matrix
get_lower_tri<-function(cormat){
  cormat[upper.tri(cormat)] <- NA
  return(cormat)
}

# Get upper triangle of the correlation matrix
get_upper_tri <- function(cormat){
  cormat[lower.tri(cormat)]<- NA
  return(cormat)
}

dg <- df[df$state == 9, ]
du <- df[df$state == 44, ]

cormat <- (round(cor(dg[, c(5,6,7,8,9)]), 2))
melted_df <- melt(cormat, na.rm=TRUE)
ggplot(data = melted_df, aes(x=Var1, y=Var2, fill=value)) + 
  geom_tile(color = "white")+
  ggtitle("Correlation matrix for Connecticut") + 
  scale_fill_gradient2(low = "blue", high = "red", mid = "white", 
                       midpoint = 0, limit = c(-1,1), space = "Lab", 
                       name="Pearson\nCorrelation") +
  geom_text(aes(Var2, Var1, label = value), color = "black", size = 4) + 
  theme_minimal()+
  theme( 
    axis.title.x = element_blank(),
    axis.title.y = element_blank(),
    plot.title = element_text(face="bold")
  ) +
  coord_fixed()


cormat <- (round(cor(du[, c(5,6,7,8,9)]), 2))
melted_df <- melt(cormat, na.rm=TRUE)
ggplot(data = melted_df, aes(x=Var1, y=Var2, fill=value)) + 
  geom_tile(color = "white")+
  ggtitle("Correlation matrix for Utah") + 
  scale_fill_gradient2(low = "blue", high = "red", mid = "white", 
                       midpoint = 0, limit = c(-1,1), space = "Lab", 
                       name="Pearson\nCorrelation") +
  geom_text(aes(Var2, Var1, label = value), color = "black", size = 4) + 
  theme_minimal()+
  theme( 
    axis.title.x = element_blank(),
    axis.title.y = element_blank(),
    plot.title = element_text(face="bold")
  ) +
  coord_fixed()
