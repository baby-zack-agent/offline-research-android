# Demo transcript — Offline AI Research App (poidh bounty #31)

Generated: 2026-10-13T13:45:35.956719+00:00
Knowledge pack: pack-v1.db — 155 documents, 14.2 MB, FTS5-indexed
Engine: extractive RAG (FTS5 BM25 retrieval + sentence ranking + cited templates).
Runtime: 100% offline, zero network calls, zero inference weights.

## Q1 — FACTUAL (baseline)

**Query:** What is the photoelectric effect and who explained it?

**Type detected:** FACTUAL · **engine time:** 128 ms · **sources used:** 2

## Answer

Quantum mechanics arose gradually from theories to explain observations that could not be reconciled with classical physics, such as Max Planck's solution in 1900 to the black-body radiation problem, and the correspondence between energy and frequency in Albert Einstein's 1905 paper, which explained the photoelectric effect. [1]

Quantum tunnelling has several important consequences, enabling radioactive decay, nuclear fusion in stars, and applications such as scanning tunnelling microscopy, tunnel diode and tunnel field-effect transistor. [1]

Einstein's formula, however simple, explained all the phenomenology of the photoelectric effect, and had far-reaching consequences in the development of quantum mechanics. [2]

In 1905, Albert Einstein proposed a theory of the photoelectric effect using a concept that light consists of tiny packets of energy known as photons or light quanta. [2]

In 1887, Heinrich Hertz observed the photoelectric effect and reported on the production and reception of electromagnetic waves. [2]

**Sources**
[1] Quantum mechanics
[2] Photoelectric effect

---

## Q2 — EXPLANATION

**Query:** Explain how quantitative easing works and how it differs from the money printing that caused hyperinflation in the Weimar Republic.

**Type detected:** EXPLANATION · **engine time:** 129 ms · **sources used:** 2

## Explanation

Hyperinflation affected the German Papiermark, the currency of the Weimar Republic, between 1921 and 1923, primarily in 1923. [1]

Hyperinflation caused considerable internal political instability in the country. [1]

Historians and economists are divided on the causes of this hyperinflation, particularly the extent to which it was caused by reparations payments. [1]

According to economist Robert McTeer, former president of the Federal Reserve Bank of Dallas, there is nothing wrong with printing money during a recession, and quantitative easing is different from traditional monetary policy "only in its magnitude and pre-announcement of amount and timing". [2]

Conversely, the post COVID-19 economy, which faced increased inflation due to excessive quantitative easing, has been addressed through quantitative tightening measures. [2]

Central banks usually resort to quantitative easing when interest rates approach zero, such as in 2008 and 2020 for the US and in 1999 for Japan. [2]

**Sources**
[1] Hyperinflation in the Weimar Republic
[2] Quantitative easing

---

## Q3 — COMPARISON (hard: 1B models conflate these)

**Query:** Compare the causes of the Great Depression and the 2008 financial crisis.

**Type detected:** COMPARISON · **engine time:** 57 ms · **sources used:** 2

## Comparison: Great Depression vs 2008 financial crisis

| Aspect | Great Depression | 2008 financial crisis |
|---|---|---|
| **Overview** | The Great Depression was a severe global economic downturn from 1929 to 1939. [1] | A major worldwide financial crisis centered in the United States took place in 2008. [2] |
| **Causes / origins** | While the precise causes for the occurrence of the Great Depression are disputed and can be traced to both global and national phenomena, its immediate origins are most conveniently examined in the context of the U.S. economy, from which the initial crisis spread to the rest of the world.; They argued that the Great Depression was caused by the banking crisis that caused one-third of all banks to vanish, a reduction of bank shareholder wealth, and more importantly, a monetary contraction of 35%, which they called "The Great Contraction". [1] | While the causes of the bubble and subsequent crash are disputed, the precipitating factor for the Financial Crisis of 2007–2008 was the bursting of the United States housing bubble and the subsequent subprime mortgage crisis, which occurred due to a high default rate and resulting foreclosures of mortgage loans, particularly adjustable-rate mortgages.; Easy availability of credit in the US, fueled by large inflows of foreign funds after the 1998 Russian financial crisis and 1997 Asian financial crisis of the 1997–1998 period, led to a housing construction boom and facilitated debt-financed consumer spending. [2] |
| **Key dates & figures** | The financial crisis now caused a major political crisis in Britain in August 1931.; This led to a financial crisis peaking in 1932 and major government intervention. [1] | Since the 2008 financial crisis, consumer regulators in America have more closely supervised sellers of credit cards and home mortgages in order to deter anticompetitive practices that led to the crisis.; A liquidity crisis spread to global institutions by mid-2007 and climaxed with the bankruptcy of Lehman Brothers in September 2008, which triggered a stock market crash and bank runs in several countries. [2] |
| **Outcomes / legacy** | John Maynard Keynes did not think that the New Deal under Roosevelt single-handedly ended the Great Depression: "It is, it seems, politically impossible for a capitalistic democracy to organize expenditure on the scale necessary to make the grand experiments which would prove my case—except in war conditions."

According to Christina Romer, the money supply growth caused by huge international gold inflows was a crucial source of the recovery of the United States economy, and the economy showed little sign of self-correction.; At the beginning of the Great Depression, most economists believed in Say's law and the equilibrating powers of the market and failed to understand the severity of the Depression. [1] | October 14, 2008: Having been suspended for three successive trading days (October 9, 10 and 13), the Icelandic stock market reopened on October 14, with the main index, the OMX Iceland 15, closing at 678.4, which was about 77% lower than the 3,004.6 at the close on October 8, after the value of the three big banks, which had formed 73.2% of the value of the OMX Iceland 15, had been set to zero, leading to the 2008–2011 Icelandic financial crisis.; Lack of investor confidence in bank solvency and declines in credit availability led to plummeting stock and commodity prices in late 2008 and early 2009. [2] |

**In short:** While the precise causes for the occurrence of the Great Depression are disputed and can be traced to both global and national phenomena, its immediate origins are most conveniently examined in the context of the U.S. economy, from which the initial crisis spread to the rest of the world. [1] By contrast, While the causes of the bubble and subsequent crash are disputed, the precipitating factor for the Financial Crisis of 2007–2008 was the bursting of the United States housing bubble and the subsequent subprime mortgage crisis, which occurred due to a high default rate and resulting foreclosures of mortgage loans, particularly adjustable-rate mortgages. [2]

**Sources**
[1] Great Depression
[2] 2008 financial crisis

---

## Q4 — COMPARISON (hard: 271 years apart, often confused)

**Query:** What were the key differences between the Treaty of Versailles and the Treaty of Westphalia?

**Type detected:** COMPARISON · **engine time:** 75 ms · **sources used:** 2

## Comparison: Treaty of Versailles vs Treaty of Westphalia

| Aspect | Treaty of Versailles | Treaty of Westphalia |
|---|---|---|
| **Overview** | The Treaty of Versailles was a peace treaty signed on 28 June 1919. [1] | The Peace of Westphalia (, ) is the collective name for two peace treaties signed in October 1648 in the Westphalian cities of Osnabrück and Münster. [2] |
| **Causes / origins** | Foreign minister Hermann Müller and colonial minister Johannes Bell travelled to Versailles to sign the treaty on behalf of Germany.; It was signed in the Palace of Versailles, exactly five years after the assassination of Archduke Franz Ferdinand, the proximate cause of the war. [1] | Westphalia also called for 50 judges to be appointed, but this number was rarely reached due to financial issues.; Talks took place in two cities because each side wanted to meet on territory under its own control. [2] |
| **Key dates & figures** | Foodstuffs imports into Germany were controlled by the Allies after the Armistice with Germany until Germany signed the Treaty of Versailles in June 1919.; The treaty restored the provinces of Alsace-Lorraine to France by rescinding the treaties of Versailles and Frankfurt of 1871 as they pertained to this issue. [1] | The Swiss Confederacy attained legal independence from the Holy Roman Empire, although it had been de facto independent since the Treaty of Basel (1499).; Fighting continued between France and Spain until the Treaty of the Pyrenees in 1659. [2] |
| **Outcomes / legacy** | In Article 231 Germany accepted responsibility for the losses and damages caused by the war "as a consequence of the ... aggression of Germany and her allies." The treaty required Germany to compensate the Allied powers, and it also established an Allied "Reparation Commission" to determine the exact amount which Germany would pay and the form that such payment would take.; Although the armistice of 11 November 1918 ended the actual fighting, and agreed certain principles and conditions including the payment of reparations, it took six months of Allied negotiations at the Paris Peace Conference to conclude the peace treaty. [1] | They ended the Thirty Years' War (1618–1648) and brought peace to the Holy Roman Empire, closing a calamitous period of European history that killed between 4.5 and 8 million people.; The Peace of Prague (1635) ended most religious aspects of the war, and the French–Habsburg rivalry took over prominence. [2] |

**In short:** Foreign minister Hermann Müller and colonial minister Johannes Bell travelled to Versailles to sign the treaty on behalf of Germany. [1] By contrast, Westphalia also called for 50 judges to be appointed, but this number was rarely reached due to financial issues. [2]

**Sources**
[1] Treaty of Versailles
[2] Treaty of Westphalia

---

## Q5 — SYNTHESIS (multi-hop: two experiments -> one conclusion)

**Query:** Using the Michelson-Morley experiment and the photoelectric effect, explain how both challenged classical physics.

**Type detected:** SYNTHESIS · **engine time:** 65 ms · **sources used:** 4

## Synthesis

**Evidence — Length contraction:** Length contraction was postulated by George FitzGerald (1889) and Hendrik Antoon Lorentz (1892) to explain the negative outcome of the Michelson–Morley experiment and to rescue the hypothesis of the stationary aether (Lorentz–FitzGerald contraction hypothesis). [1] Although both FitzGerald and Lorentz alluded to the fact that electrostatic fields in motion were deformed ("Heaviside-Ellipsoid" after Oliver Heaviside, who derived this deformation from electromagnetic theory in 1888), it was considered an ad hoc hypothesis, because at this time there was no sufficient reason to assume that intermolecular forces behave the same way as electromagnetic ones. [1]

**Evidence — Quantum mechanics:** Quantum mechanics arose gradually from theories to explain observations that could not be reconciled with classical physics, such as Max Planck's solution in 1900 to the black-body radiation problem, and the correspondence between energy and frequency in Albert Einstein's 1905 paper, which explained the photoelectric effect. [2] Classical physics can describe many aspects of nature at an ordinary (macroscopic and (optical) microscopic) scale; however, it is insufficient for describing them at very small submicroscopic (atomic and subatomic) scales. [2]

**Evidence — Double-slit experiment:** In modern physics, the double-slit experiment demonstrates that light and matter can exhibit behavior associated with both classical particles and classical waves. [3] In 1974, the Italian physicists , Gian Franco Missiroli, and Giulio Pozzi performed a related experiment using single electrons from a coherent source and a biprism beam splitter, showing the statistical nature of the buildup of the interference pattern, as predicted by quantum theory. [3]

**Evidence — Wave–particle duality:** In 1905 Albert Einstein interpreted the photoelectric effect also with discrete energies for photons. [4] However, the wave model was challenged in 1901 by Planck's law for black-body radiation. [4]

**Putting it together:** Quantum mechanics arose gradually from theories to explain observations that could not be reconciled with classical physics, such as Max Planck's solution in 1900 to the black-body radiation problem, and the correspondence between energy and frequency in Albert Einstein's 1905 paper, which explained the photoelectric effect. [2] Length contraction was postulated by George FitzGerald (1889) and Hendrik Antoon Lorentz (1892) to explain the negative outcome of the Michelson–Morley experiment and to rescue the hypothesis of the stationary aether (Lorentz–FitzGerald contraction hypothesis). [1] In modern physics, the double-slit experiment demonstrates that light and matter can exhibit behavior associated with both classical particles and classical waves. [3]

**Sources**
[1] Length contraction
[2] Quantum mechanics
[3] Double-slit experiment
[4] Wave–particle duality

---

## Q6 — REASONING

**Query:** Why did the Bretton Woods system collapse?

**Type detected:** REASONING · **engine time:** 14 ms · **sources used:** 2

## Analysis

The Bretton Woods system of monetary management established the rules for commercial relations among 44 countries, including the United States, Canada, European countries, and Australia, after the 1944 Bretton Woods Agreement until the Jamaica Accords in 1976. [1]

The Bretton Woods system played a key role in shaping the postwar global economy, but its structure also led to significant challenges. [1]

This proved to be the beginning of the collapse of the Bretton Woods System. [1]

The Nixon shock also indirectly led to the development of SWIFT, as the collapse of Bretton Woods and the shift to floating exchange rates exposed weakness in the telex-based system. [2]

In 1944, representatives from 44 nations met in Bretton Woods, New Hampshire, to develop a new international monetary system that came to be known as the Bretton Woods system. [2]

The Bretton Woods system became fully operational by 1958. [2]

**Sources**
[1] Bretton Woods system
[2] Nixon shock

---

## Q7 — COMPARISON

**Query:** Compare nuclear fission and nuclear fusion as energy sources.

**Type detected:** COMPARISON · **engine time:** 102 ms · **sources used:** 2

## Comparison: Nuclear fission vs Nuclear fusion

| Aspect | Nuclear fission | Nuclear fusion |
|---|---|---|
| **Overview** | Nuclear fission is a reaction in which the nucleus of an atom splits into two or more smaller nuclei. [1] | Nuclear fusion is a reaction in which two or more atomic nuclei combine to form a larger nucleus. [2] |
| **Causes / origins** | Energy of about 6 MeV provided by the incident neutron was necessary to overcome this barrier and cause the nucleus to fission.; For uranium-235 (total mean fission energy 202.79 MeV), typically ~169 MeV appears as the kinetic energy of the daughter nuclei, which fly apart at about 3% of the speed of light, due to Coulomb repulsion. [1] | A nuclear fusion process that produces atomic nuclei lighter than nickel-62 is generally exothermic, due to the positive gradient of the nuclear binding energy curve.; A search for new ideas led to the Teller-Ulam design, named after Teller and Stanislaw Ulam, which used the radiation energy of a fission bomb to highly compress (radiation implosion) the fusion fuel prior to its ignition. [2] |
| **Key dates & figures** | Spontaneous fission, discovered in 1940 by Georgy Flyorov, Konstantin Petrzhak, and Igor Kurchatov, is fission not induced by an exogenous neutron, but rather a spontaneous radioactive decay occurring because the nucleus is already unstable from an overabundance of neutrons, and occurs in very high-mass-number isotopes.; However, not all were convinced by Fermi's analysis of his results, though he would win the 1938 Nobel Prize in Physics for his "demonstrations of the existence of new radioactive elements produced by neutron irradiation, and for his related discovery of nuclear reactions brought about by slow neutrons". [1] | Private companies pursuing the commercialization of nuclear fusion received $2.6 billion in private funding in 2021 alone, going to many notable startups including but not limited to Commonwealth Fusion Systems, Helion Energy Inc., General Fusion, TAE Technologies Inc. and Zap Energy Inc.; The concept dates to the 1950s, and was briefly advocated by Hans Bethe during the 1970s, but largely remained unexplored until a revival of interest in 2009, due to the delays in the realization of pure fusion. [2] |
| **Outcomes / legacy** | In this case, the first experimental atomic reactors would have run away to a dangerous and messy "prompt critical reaction" before their operators could have manually shut them down (for this reason, designer Enrico Fermi included radiation-counter-triggered control rods, suspended by electromagnets, which could automatically drop into the center of Chicago Pile-1). [1] | Being just the second fusion bomb ever tested (and the first to use lithium), the designers of the Castle Bravo "Shrimp" had understood the usefulness of 6Li in tritium production, but had failed to recognize that 7Li fission would greatly increase the yield of the bomb.; The sun, magnetically confined plasmas and inertial confinement fusion systems are well modeled to be in thermal equilibrium. [2] |

**In short:** Energy of about 6 MeV provided by the incident neutron was necessary to overcome this barrier and cause the nucleus to fission. [1] By contrast, A nuclear fusion process that produces atomic nuclei lighter than nickel-62 is generally exothermic, due to the positive gradient of the nuclear binding energy curve. [2]

**Sources**
[1] Nuclear fission
[2] Nuclear fusion

---

## Q8 — EXPLANATION

**Query:** Explain how natural selection produces new species over time.

**Type detected:** EXPLANATION · **engine time:** 232 ms · **sources used:** 2

## Explanation

However, natural selection remained controversial as a law or mechanism, partly because it was perceived to be too weak to explain the range of observed characteristics of living organisms, and partly because even supporters of evolution balked at its "unguided" and non-progressive nature, a response that has been characterised as the single most significant impediment to the idea's acceptance. [1]

Natural selection is the differential survival and reproduction of individuals due to differences in the relative fitness endowed on them by their own particular complement of observable characteristics. [1]

The concept, published by Darwin and Alfred Russel Wallace in a joint presentation of papers in 1858, was elaborated in Darwin's influential 1859 book On the Origin of Species by Means of Natural Selection, or the Preservation of Favoured Races in the Struggle for Life. [1]

At the end of 1859, Darwin's publication of his "abstract" as On the Origin of Species explained natural selection in detail and in a way that led to an increasingly wide acceptance of Darwin's concepts of evolution at the expense of alternative theories. [2]

In 1751, Pierre Louis Maupertuis wrote of natural modifications occurring during reproduction and accumulating over many generations to produce new species. [2]

This can be important when one allele in a particular haplotype is strongly beneficial: natural selection can drive a selective sweep that will also cause the other alleles in the haplotype to become more common in the population; this effect is called genetic hitchhiking or genetic draft. [2]

**Sources**
[1] Natural selection
[2] Evolution

---

## Q9 — SYNTHESIS (cross-century pattern)

**Query:** What do the South Sea Bubble and the dot-com bubble imply about the recurring causes of financial bubbles?

**Type detected:** SYNTHESIS · **engine time:** 83 ms · **sources used:** 4

## Synthesis

**Evidence — Dot-com bubble:** The dot-com bubble (or dot-com boom) was a stock market bubble that developed during the late 1990s and peaked on March 10, 2000. [1] During the dot-com crash, many online shopping companies like Pets.com, Webvan, and Boo.com, as well as several communication companies, such as WorldCom, NorthPoint Communications, and Global Crossing, failed and shut down; WorldCom was renamed to MCI Inc. in 2003 and was acquired by Verizon in 2006. [1]

**Evidence — South Sea Bubble:** South Sea Bubble collection at Harvard University
 Famous First Bubbles – South Sea Bubble
 
 
 The South Sea Bubble, audio programming with Melvyn Bragg and guests, BBC Radio 4. [2] David Liss' historical-mystery novel A Conspiracy of Paper, set in 1720 London, is focused on the South Sea Company at the top of its power, its fierce rivalry with the Bank of England and the events leading up to the collapse of the "bubble". [2]

**Evidence — Subprime mortgage crisis:** In its "Declaration of the Summit on Financial Markets and the World Economy," dated November 15, 2008, leaders of the Group of 20 cited the following causes:

Federal Reserve Chair Ben Bernanke testified in September 2010 regarding the causes of the crisis. [3] The U.S. government intervened with a series of measures to stabilize the financial system, including the Troubled Asset Relief Program (TARP) and the American Recovery and Reinvestment Act of 2009 (ARRA). [3]

**Evidence — 2008 financial crisis:** While the causes of the bubble and subsequent crash are disputed, the precipitating factor for the Financial Crisis of 2007–2008 was the bursting of the United States housing bubble and the subsequent subprime mortgage crisis, which occurred due to a high default rate and resulting foreclosures of mortgage loans, particularly adjustable-rate mortgages. [4] Economist Paul Krugman argued in January 2010 that the simultaneous growth of the residential and commercial real estate pricing bubbles and the global nature of the crisis undermines the case made by those who argue that Fannie Mae, Freddie Mac, CRA, or predatory lending were primary causes of the crisis. [4]

**Putting it together:** South Sea Bubble collection at Harvard University
 Famous First Bubbles – South Sea Bubble
 
 
 The South Sea Bubble, audio programming with Melvyn Bragg and guests, BBC Radio 4. [2] While the causes of the bubble and subsequent crash are disputed, the precipitating factor for the Financial Crisis of 2007–2008 was the bursting of the United States housing bubble and the subsequent subprime mortgage crisis, which occurred due to a high default rate and resulting foreclosures of mortgage loans, particularly adjustable-rate mortgages. [4] David Liss' historical-mystery novel A Conspiracy of Paper, set in 1720 London, is focused on the South Sea Company at the top of its power, its fierce rivalry with the Bank of England and the events leading up to the collapse of the "bubble". [2]

**Sources**
[1] Dot-com bubble
[2] South Sea Bubble
[3] Subprime mortgage crisis
[4] 2008 financial crisis

---

## Q10 — FACTUAL (baseline)

**Query:** When did the Berlin Wall fall and what did it symbolize?

**Type detected:** FACTUAL · **engine time:** 23 ms · **sources used:** 1

## Answer

Although other factors were probably more influential in the fall of the Wall,

On 19 July 1988, 16 months before the Wall came down, Bruce Springsteen and the E Street Band, played Rocking the Wall, a live concert in East Berlin, which was attended by 300,000 in person and broadcast on television. [1]

Thirty years after the fall of the Berlin Wall, The Guardian collected short stories from 9 November 1989 by five German writers who reflect on the day. [1]

Construction of the Berlin Wall was commenced by the government of the GDR on 13 August 1961. [1]

**Sources**
[1] Berlin Wall

---

**Total engine time for 10 queries: 908 ms (avg 91 ms/query).**
