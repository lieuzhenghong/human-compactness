## Motivation

Good job today. To reiterate, basically I think your research question should
be something like: "Research shows that districts that consist of more
homogeneous groups of voters achieve better representation on several
dimensions. Meanwhile, many statutes require that districts be "compact", a
term with many interpretations. It is not clear, however, that more compact
districting plans (however compactness is measured) result in more homogeneous
districts. Are compactness and homogeneity fundamentally conflicting goals? Are
some measures of compactness more consistent with homogeneity than others?"      

## Strategy

1. Spatial diversity is bad, homogeneity good
2. States legally mandate compactness
3. Might commonly-used compactness measures exacerbate spatial diversity (bad),
	 actually give us more homogeneous districts (good), or do nothing at all?
	 The answer to this question is an empirical one. Further, if different
	 compactness measures track spatial diversity differently, that may give us a
	 prima facie reason to select one over the other (apart from their ability to
	 measure gerrymandering).
4. I answer these empirical questions through MCMC methods + a novel method of
	 compactness developed with Rodden and Eubank. (human compactness as a
	 robustness measure --- using driving distances rather than geometric
	 compactness measures should give different findings if the relationship
	 between compactness and spatial diversity is specific to geometric
	 compactness measures)
5. I find that compactness measures and spatial diversity measures are largely
	 orthogonal. These are mixed results. It's encouraging that compactness is
	 not making the problem worse, but sad that more compact districts can't have
	 better democratic outcomes.
	 - I also find, reassuringly, that various compactness measures track each
		 other well, including human compactness and geographic compactness
		 measures
	 - There is some weak evidence to suggest that human compactness outperforms
		 geographic compactness in certain special cases.
6. Further work can build upon my same methodology to investigate the
	 relationship between compactness metrics and the seat-vote curve (King
	 2020), Moon and Deford 2019
7. My contribution: methodological and empirical (no more theoretical bit about
	 why compactness matters --- where to fit in?)
8. I present a theoretical model showing under what circumstances different
	 compactness measures can increase/decrease spatial diversity

Present two (three?) different views of compactness metric.

- One is that compactness metrics could track spatial diversity. Given that we
	know that regions are not arranged in a "checkerboard" position, districts
	that are compact must contain large homogeneous(ish) clusters. Therefore,
	compactness should track spatial diversity.

- The other is that compactness does nothing to track spatial diversity... for
	reasons elucidated below 

- Could compactness even result in *more* spatially diverse districts? Would
	optimising for compactness inadvertently throw people from very different
	backgrounds together, ignoring natural boundaries, communities, etc... all in
	the pursuit of a nice square/rectangle shape?
		- of course, it probably wouldn't be the case that a random plan that
			*wasn't* compact would be any more likely to respect natural boundaries
			and communities, so I don't think this is true.

Present four different compactness metrics

Then talk about my method for answering this question.
	1. Theorise and talk about computing HC
	2. MCMC methods

Then give the findings.

Show the cool visualisations

## Findings

Top line findings: compactness measures and spatial diversity are largely
orthogonal, at least at the level of the plan. There is some (weak) evidence
that human-compactness is superior to regular compactness scores

Even at the level of the district, we find that compactness measures don't
track spatial diversity well. There are a couple reasons for this:

1. Small districts (districts that basically just are a city) are always more
	 spatially diverse, no matter how one tries to draw them. (Check the KDE
	 plots).
2. Geographical measures of compactness want districts to be drawn in the shape
	 of nice rectangles and squares. But there is no reason why cities/people of
	 different types should follow nice squares. See for instance Idaho (16).
	 People are distributed in a U-shape. Same with Utah (49): people are
	 distributed in a long line that seems to follow a river?
3. Human compactness wants to keep people close together in the same district,
	 which works well for cities. But people who live far away can be
	 homogeneous, and people who live close together (i.e in a city) can be
	 heterogeneous. Spatial diversity will want to snake around and grab all the
	 city-dwellers/poor people/white people, and that can go against compactness.
4. Basically it boils down to this: is seems to be just as likely for a weird
	 snakey uncompact shape to be of high spatial diversity, as it is of low
	 spatial diversity. If we're talking about within a city, then yes
	 definitely: but if we're talking about the level of a state, then a snakey
	 shape that grabs two separate population centers will be good. See Idaho for
	 an example.
5. Human compactness however works well when people are more or less
	 homogeneous and the population is either evenly-spread or there's only one
	 big population center or population centers are not too far away.

Even though compactness is orthogonal, we may still like it for several
reasons: prevents gerrymandering, keeps neighbourhoods together in the same
district (implications for political participation?)

Nonetheless, given that we know that spatial diversity is important,
districting for compactness is not going to get us there.

**Could Stephanopoulos be picking up a urban-rural divide effect?**


But Stephanopoulos controls for top-line diversity.... so how are his findings
still significant.... 

> Controlling for districts’ scores on the Sullivan Index (incorporating
data on race, ethnicity, age, income, education, profession, marital status,
and housing), 199 spatial diversity again remained a statistically significant
predictor of roll-off rate. 200 

But Stephanopoulos himself says:

> However, this is not a perfect control since the level of top-line diversity
> still varies between
(as opposed to within) the two samples.


## What spatial diversity is

At the national level, the factor with the greatest explanato- ry power is
primarily a function of raw variables relating to income, education, and
profession. It distinguishes tracts whose residents are well-educated, wealthy
professionals from tracts whose residents have the opposite characteristics.
The next most significant factor corre- sponds largely to marital and
residential situation. It differentiates be- tween tracts of married
home-owners (mostly suburbs and rural areas) and tracts of unmarried
apartment-dwellers (mostly cities). The third, fourth, and fifth factors all
revolve around race. They indicate, re- spectively, the proportions of tracts’
populations that are Hispanic, Af- rican American, and Asian American. The
sixth factor identifies tracts with white ethnic residents living in older
housing stock. The seventh factor is mostly a measure of age. Lastly, the
eighth factor tells apart tracts with heavily agricultural workforces from
tracts whose econo- mies are more service-oriented. These findings are
consistent with those of other researchers, 180 and are presented more fully
in Tablein the Appendix. 181

In this section, I assess the claim and I find that it is largely correct. The
rate of voter roll-off is substantial- ly higher in spatially diverse
districts, while the link between politi- cians’ voting records and their
constituents’ interests is substantially weaker. Representatives from
spatially diverse districts also have more polarized voting records than their
counterparts from spatially homogeneous districts.

 To the extent that these characteristics capture salient political
interests, the implication is that representation was less responsive in
the highly heterogeneous districts. Elected officials in these districts
voted more often in ways that were unrelated to (or at least unpredict-
ed by) their constituents’ apparent interests. 20

<--- this is at the district level. Can we say anything on the plan level?

##  Obtaining the results

A custom aggregation function: take the square root


## Interpretation of results

Spatial diversity scores don't vary much:


At the district level, compactness measures all agree with one another quite
well.

But at the aggregate level, they don't always agree. The geographic compactness
measures do agree with each other, but they don't always agree with the human
compactness metric.
	--> probably because of cities


To be sure, correlation is
often

First, compactness measures all track spatial diversity quite well, to the tune
of anywhere between ~0.3 to 

The correspondence between compactness measures of spatial diversity 


In New Hampshire (state 33), human compactness outperforms

New Hampshire is an almost all-white state.

but so is Idaho


### Optimising over compactness measures

## Oopsies

Figures 12 and 13 show how states’ spatial diversity averages were
related to partisan bias and electoral responsiveness in the 2006, 2008,
and 2010 elections.260 I include only states with at least ten congres-
sional districts (because bias and responsiveness are not very meaning-
ful for states with small numbers of seats),261 and I use the absolute
value of bias (because I am interested in the metric’s magnitude rather
than its orientation). As is evident from the first chart, spatial diversi-
ty has a curvilinear relationship with bias. At lower levels of spatial
diversity, that is, bias tends to decrease as spatial diversity increases;
but at higher levels of spatial diversity, bias and spatial diversity tend
to move in tandem. The curve as a whole is clearly U-shaped. 262

This result suggests that states seeking to treat the major parties as
equitably as possible should not minimize the average spatial diversity
of their districts. Consistent with the relevant literature, high levels of
geographic variation are associated with high bias; 263 they both imply
that traditional districting criteria have been neglected, and enable the
execution of the optimal “matching slices” gerrymandering strategy —
by which groups of one party’s voters are paired with slightly smaller
groups of the opposing party’s voters.264 But low levels of variation
are linked to high bias as well, presumably because parties’ supporters
are excessively “packed” when most districts are very homogeneous.
The ideal level of spatial diversity (in that it minimizes bias) appears to
lie in the center of the distribution — not so high that natural geo-
graphic alignments are swept aside for the sake of partisan advantage,
but not so low that the parties’ devotees end up overconcentrated. At
this Goldilocks position, neither of the usual gerrymandering strat-
egies can be carried out to full effect, and partisan fairness reaches its
apogee.

The story with responsiveness is more straightforward. As the se-
cond chart illustrates, responsiveness simply tends to decrease as aver-
age spatial diversity increases. The states whose districts are most
homogeneous, on average, are also the states whose elections are most
responsive to changes in public opinion. In contrast, the states whose
districts are most heterogeneous are also the ones in which even large
swings in voter sentiment have little impact on the parties’ seat shares.
This finding indicates that while high spatial diversity is not a prereq-
uisite for a partisan gerrymander (low spatial diversity can also do the
trick), it is indeed an effective way to protect incumbents of both par-
ties from shifting political tides. Advocates of responsive elections,
then, may push without hesitation for spatially homogeneous districts
to be drawn, since it is these districts that seem most likely (in the ag-
gregate) to reflect the public’s evolving preferences. 265

## No actually

Scholars tend to think instrumentally about districts. They focus
on the implications of different districting schemes for partisan fair-
ness, electoral competition, and minority representation. These are
important issues, to be sure, but they neglect what one might call the
intrinsic aspects of constituencies: how well they correspond to geo-
graphic communities, how willing their voters are to engage in the po-
litical process, and how suitable a forum they provide for sound repre-
sentation. This Article is part of a larger project that aims to take
districts themselves seriously (and not just their electoral consequenc-
es). 308 The concept that the Article introduces, spatial diversity, shifts
the spotlight from utilitarian considerations onto districts’ actual com-
plexions. It stresses not how districts perform politically but rath-er
how they are constituted internally. It is this change in emphasis —
not any of my specific claims about spatially diverse districts — that I
consider to be the Article’s principal contribution. What districts are
like is as meaningful as who they elect.
