from manim import *
import pandas as pd

name = "TP._Ho_Chi_Minh"
df = pd.read_csv(f"./pop_dist_region/{name}.csv", index_col=0)

male_pop = [x*100/df['all_m'].iloc[0] for x in df['all_m'][1:]]
female_pop = [x*100/df['all_f'].iloc[0] for x in df['all_f'][1:]]

print(male_pop)
print(female_pop)
d_font = "Montserrat"

class PopulationPyramid(Scene):
    def construct(self):
        # Data for the population pyramid
        age_groups = df["Region"][1:][::-1]
        male_population = male_pop[::-1]
        female_population = female_pop[::-1]

        # Create ValueTracker to animate the scaling
        scale_tracker = ValueTracker(0)

        # Create bars for male population with updaters
        male_bars = VGroup(*[
            Rectangle(
                width=0, height=0.3, fill_color=BLUE, fill_opacity=0.8,
                stroke_color=BLACK, stroke_width=.5
            ).shift(LEFT * pop * 0.6 / 2 + DOWN * i * 0.4 + UP*3).add_updater(
                lambda rect, pop=pop, i=i: rect.become(
                    Rectangle(
                        width=scale_tracker.get_value() * pop * 0.6,
                        height=0.3,
                        fill_color=BLUE,
                        fill_opacity=1,
                        stroke_color=BLACK,
                        stroke_width=.5
                    ).shift(LEFT * scale_tracker.get_value() * pop * 0.6 / 2 + DOWN * i * 0.4 + UP*3)
                )
            )
            for i, pop in enumerate(male_population)
        ])

        # Create bars for female population with updaters
        female_bars = VGroup(*[
            Rectangle(
                width=0, height=0.3, fill_color=PINK, fill_opacity=0.8,
                stroke_color=BLACK, stroke_width=.5
            ).shift(RIGHT * pop * 0.6 / 2 + DOWN * i * 0.4 + UP*5).add_updater(
                lambda rect, pop=pop, i=i: rect.become(
                    Rectangle(
                        width=scale_tracker.get_value() * pop * 0.6,
                        height=0.3,
                        fill_color=PINK,
                        fill_opacity=1,
                        stroke_color=BLACK,
                        stroke_width=.5
                    ).shift(RIGHT * scale_tracker.get_value() * pop * 0.6 / 2 + DOWN * i * 0.4 + UP*3)
                )
            )
            for i, pop in enumerate(female_population)
        ])

        # Create age labels
        age_labels_l = VGroup(*[
            Text(age, font_size=18, font=d_font).add_updater(lambda label, i=i: label.next_to(male_bars[i], LEFT, buff=0.7))
            for i, age in enumerate(age_groups)
        ])
        
        age_labels_r = VGroup(*[
            Text(age, font_size=18, font=d_font).add_updater(lambda label, i=i: label.next_to(female_bars[i], RIGHT, buff=0.7))
            for i, age in enumerate(age_groups)
        ])

        # Create population labels for males with updaters
        male_labels = VGroup(*[
            Text("", font_size=18, font=d_font).next_to(male_bars[i], RIGHT, buff=0.1).add_updater(
                lambda label, pop=pop, i=i: label.become(
                    Text(f"{scale_tracker.get_value() * pop:.1f}%", font_size=18, font=d_font).next_to(male_bars[i], RIGHT, buff=0.1)
                )
            )
            for i, pop in enumerate(male_population)
        ])

        # Create population labels for females with updaters
        female_labels = VGroup(*[
            Text("", font_size=18, font=d_font).next_to(female_bars[i], LEFT, buff=0.1).add_updater(
                lambda label, pop=pop, i=i: label.become(
                    Text(f"{scale_tracker.get_value() * pop:.1f}%", font_size=18, font=d_font).next_to(female_bars[i], LEFT, buff=0.1)
                )
            )
            for i, pop in enumerate(female_population)
        ])
        
        # Add all elements to the scene
        self.add(female_bars, male_bars, male_labels, female_labels)

        # Animate the scaling
        anim = LaggedStart(*[DrawBorderThenFill(age_labels_l), DrawBorderThenFill(age_labels_r)], lag_ratio=0.4)
        self.play(scale_tracker.animate.set_value(1), run_time=2, rate_func=rate_functions.ease_in_out_cubic)
        self.play(anim, run_time=2, rate_func=rate_functions.ease_in_out_cubic)

