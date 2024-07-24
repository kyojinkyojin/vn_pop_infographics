from manim import *
import pandas as pd

name = "TP._Ho_Chi_Minh"
df = pd.read_csv(f"./pop_dist_region/{name}.csv", index_col=0)

male_pop = [x*100/df['all_m'].iloc[0] for x in df['all_m'][1:]]
female_pop = [x*100/df['all_f'].iloc[0] for x in df['all_f'][1:]]

print(male_pop)
print(female_pop)

class PopulationPyramid(Scene):
    def construct(self):
        # Data for the population pyramid
        age_groups = df["Region"][1:][::-1]
        male_population = male_pop[::-1]
        female_population = female_pop[::-1]
        # Create bars for male population
        scale_tracker = ValueTracker(0)
        male_bars = VGroup(*[
            Rectangle(
                width=pop*.8, height=0.5, fill_color=BLUE, fill_opacity=0.8,
                stroke_color=BLACK, stroke_width=1
            ).shift(LEFT * pop*.8/2+ DOWN * i * 0.6).add_updater(
                lambda rect, pop=pop: rect.become(
                    Rectangle(
                        width=scale_tracker.get_value() * pop*.8,
                        height=0.5,
                        fill_color=BLUE,
                        fill_opacity=0.8,
                        stroke_color=BLACK,
                        stroke_width=1
                    ).shift(LEFT * scale_tracker.get_value() * pop*.8/2 + DOWN * i * 0.6)
                )
            )
            for i, pop in enumerate(male_population)
        ])

        # Create bars for female population
        female_bars = VGroup(*[
            Rectangle(
                width=pop*.8, height=0.5, fill_color=PINK, fill_opacity=0.8,
                stroke_color=BLACK, stroke_width=1
            ).shift(RIGHT * pop*.8/2 + DOWN * i * 0.6)
            for i, pop in enumerate(female_population)
        ])

        # Create age labels
        age_labels_l = VGroup(*[
            Text(age, font_size=18).next_to(male_bars[i], LEFT, buff=.7)
            for i, age in enumerate(age_groups)
        ])
        
        age_labels_r = VGroup(*[
            Text(age, font_size=18).next_to(female_bars[i], RIGHT, buff=.7)
            for i, age in enumerate(age_groups)
        ])

        # Create population labels for males
        male_labels = VGroup(*[
            Text(f"{'{0:.2f}'.format(pop)}%", font_size=18).next_to(male_bars[i], RIGHT, buff=0.1)
            for i, pop in enumerate(male_population)
        ])

        # Create population labels for females
        female_labels = VGroup(*[
            Text(f"{'{0:.2f}'.format(pop)}%", font_size=18).next_to(female_bars[i], LEFT, buff=0.1)
            for i, pop in enumerate(female_population)
        ])
        all = VGroup(male_bars, female_bars, age_labels_r, age_labels_l, male_labels, female_labels)
        # Add all elements to the scene
        self.add(male_bars)#.scale(.6).shift(UP*5))
        self.play(scale_tracker.animate.set_value(10), run_time=3, rate_func=linear)
        #self.add(all.scale(.6).shift(UP*5))

        # Add titles
        #male_title = Text("Male Population", font_size=30).to_edge(LEFT)
        #female_title = Text("Female Population", font_size=30).to_edge(RIGHT)
        #self.add(male_title, female_title)
