# BiathlonAzzurro
Repository for the work done for the [Biathlon Azzurro](https://biathlonazzurro.it) site.

Since joining the wonderful [Biathlon Azzurro](https://biathlonazzurro.it) team, where we passionately follow and report about the summer and winter biathlon competitions :ski: :gun:, all the analysis done has been uploaded into this Repo.
Most of teh work has been carried on through a Bayesian approach while the standard frequentist one is rarely featured. Machine Learning is also used in some of the work.
The full articles, that do not contain any code or mathematical part can be found in the [site](https://biathlonazzurro.it), the topics treated are summed up in the following:

- **Relative Age Effect (RAE)**: the world cup athletes since the 1990-1991 season have been analyze to inspect the presence of the Relative Age Effect (RAE) in a sport where there is no literature on the matter.
Biathlon is an interesting sport to inquire about RAE because it is not a vary popular sport in a lot of countryes while, on the contrary, Norway and other European nations like Belarus feature an important number of practitioners

- **The last shot in an Individual**: the Individual tace is unique in the world of Biathlon as in this case a miss does not result in a penalty lap but it causes a penalty of a whole minute.
This format then is highly favourable to snipers and each single shot as a considerable weight on the final result. For all of the above and above all for what happened during Biathlon lore, the final shot of an Individual race has become legendary.
Just looking into the last 2 winter Olympics games **Tarjei Bø** and **Maxim Tsvetkov** have lost the gold medal at the very last shot.
In this analysis we want to establish if the last shot in an Individual race is really the toughest one in the sport or if all the drama leading up to it has blown out of proportion the real shot percentages.

- **Clutchness**: The idea to inspect clutchness in Biathlon has been carried on through something that we could call a medical analysis.
When establishing the effectiveness of a vaccine a farmaceutical company prepares multiple shots. Some of them contain the real vaccine while others are placebo shots, neither the patient nor the doctor knows the nature of each shot. The Efficiency of a vaccine is then computed based on the number of patients returning with the infection as $\frac{\\# \text{Placebo infected} -  \\#\text{Vaccine infected}}{\\# \text{Placebo infected}} \cdot 100 \\%$.
What we do is to take into consideration the standings entering the last shooting range. We considered pressured situations the ones were the athlete enters the range in the top 10 while all the other positions are considered without pressure.
What we want to establish is if pressure has some kind of effect on each single athlete. In order to do that we consider top 10 shots as the vaccine samples while the outside of the top 10 ones are considered placebo, after a binomial analysis we determine the effect of pressure on each single athlete.

