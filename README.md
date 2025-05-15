# Strava Data Exploration

## What am I up to?

I love cycling and data, so an opportunity to combine the two wasn't something I could easily pass up.
At the epicenter of the marriage between cycling and data lies the power meter, which unlocks a host of capabilities
for a cyclist.
Most cyclists have computers that collect and/or display data.
All of my personal data is uploaded
to Strava after each ride.
Strava provides some interesting insights around exertion, overall speed, comparison of current performance to past
performance, etc.  I, however, want to dive more deeply into the data to truly begin to assess any improvements
in my fitness level.

With the ability to precisely measure the force being applied to the pedals, we can then gauge
how hard the body is working through heart rate data.
In theory, as fitness improves, the amount of effort required to achieve any given level of power **should** decrease.

Power is crucial for measuring performance as pace, alone, is subject to many external factors that aren't under the rider's control.
Wind, for example, can raise the amount of power required to sustain any given pace by a significant amount.  150 watts on flat ground with no wind may
propel a rider along at 15 mph.  In a 10mph headwind, the amount of power required to propel that same ride at 15mph may be 180 watts.  By
analyzing the amount of force put into the pedals, we can truly understand the amount of energy being produced by the rider. When we then consider how the rider's
heart rate behaves over time at different power levels, we can better infer improvements in fitness.

This project is my attempt to add my spin on some pre-existing methods to quantify fitness improvements.
This is far from perfect, as human fitness is incredibly complex, but it is interesting for me to study, nonetheless.  My ultimate goal
is to better quantify how much stress I'm actually putting on my body, understand how my body handles and recovers from this stress, and better
understand how much to slowly increase this.  

Many cyclists often set weekly distance goals.  This can easily be manipulated, as riding 30 miles on flat ground puts much less stress on the body 
than riding 30 miles with 3500' of elevation gain.  Some cyclists opt for a weekly time limit, but this also can be manipulated with intensity, as well.
By attempting to quantify stress, I can set weekly stress goals that exist independently of both time and distance. 

## Training Stress Balance, Acute Training Load (ATL) and Chronic Training Load (CTL)

To conduct this analysis, it's necessary to understand these three terms.  Acute training load attempts to measure the "stress" or "strain" placed upon
the body over the last 7 days.  How do we measure stress/strain?  I'm glad you asked!  To fully understand this, we need to define a few terms.

#### Functional Threshold Power (FTP)

Functional threshold power is generally understood as the *maximum* power a rider can sustain for an hour.  Some definitions use 45 minutes as a time window.
Regardless, this is considered the highest power output value which can be considered "functional" in the sense that any power demand beyond this value will lead
to rapid fatigue, causing the rider to have to reduce power drastically in order to continue.  Any serious cyclist will be very familiar with this number, and
may, in fact, even obsess over it.  One would expect that increases in fitness would increase this value, or vice versa, perhaps.
. 
Measuring FTP isn't exactly an easy feat.  Each cycling training software has its own proprietary method.  Cycling computers have dedicated tests 
that require that a cyclist rides at different levels of intensity for varying periods of time.  These tests fall short on a few fronts.
First, it's very difficult to ride at a consistent intensity, unless you're on an indoor trainer.  Second, the condition of the cyclist
during the test can drastically alter the results.  A common rule of thumb is to take your maximum observed average power over a 20-minute
window, and multiply this value by 0.95.  This will get you close-ish.

For the purposes of this analysis, I'll be using the FTP value as derived from my Garmin Edge 840 device.


### Normalized Power

Normalized power is a crucial concept to understand when beginning to quantify training stress.  The word "normalized" in normalized power is not used in the
traditional or data science sense.  Normalized power is a metric created to quantify the difficulty of a workout. It's been described by some
as the power output required to recreate the exercise at a consistent power for the duration of the activity, although others refute this.

It's effectively a weighted average over time, utilizing a 30-second sliding window average power with some scaling involved.  To better explain, consider
a workout where a rider outputs a consistent 200 watts for two hours.  The average power output would be 200 watts for this workout.  Alternatively, a 
workout where a rider outputs 100 watts for one hour, and 300 watts for a second hour, would also have an average power output of 200 watts.  These two
workouts, however, are very different concerning the overall stress placed on the body.  This is what normalized power ***attempts*** to quantify.

For a given 30-second rolling average power:
$\large \frac{1}{n} \cdot \sum_{j=i}^{i+n-1} p_j$

Normalized power is calculated as:
$W = \large \sqrt[\leftroot{-2}\uproot{2}4]{ \frac{s^4}{\bar{s^4}}}\$

### Intensity Factor (IF)
Intensity Factor (IF) is a simple yet powerful metric that provides a relative measure of how intense a cycling workout was compared to the rider's own Functional Threshold Power (FTP). 
It's calculated by dividing the Normalized Power (NP) of a ride by the rider's FTP:

$IF = \frac{NP}{FTP}$

An IF of 1.0 signifies that the Normalized Power for the ride was exactly equal to the rider's FTP. This would be akin to an all-out effort lasting approximately one hour. For longer, less strenuous rides, the IF will typically be lower (e.g., 0.70-0.85 for endurance rides), while shorter, very intense efforts or interval sessions might yield an IF closer to, or even slightly above, 1.0 for the duration of those efforts, though the overall ride IF would rarely exceed 1.15 for any significant duration. IF provides a standardized way to compare the intensity of different workouts, even if they vary in duration or power profile.

### Training Stress Score (TSS)
Training Stress Score (TSS) is a composite number that takes into account both the intensity (via IF) and the duration of a training session to provide a single value representing the overall training load or "stress" of that workout. It's a cornerstone metric for many cyclists and coaches for tracking training load over time. The formula for TSS is:

$TSS = \frac{(Duration \, in \, seconds \times NP \times IF)}{(FTP \times 3600)} \times 100$

Essentially, a one-hour ride at your FTP (meaning NP = FTP, so IF = 1.0) will yield exactly 100 TSS. Longer or more intense rides will accumulate more TSS, 
while shorter or easier rides will result in lower TSS. 
For example, a two-hour ride at an IF of 0.707 (which would mean NP is about 70.7% of FTP) would also yield approximately 100 TSS. 
This score allows for a more apples-to-apples comparison of the physiological stress induced by different types of workouts, helping to manage training load and prevent overtraining or undertraining. 
It's the foundation upon which ATL and CTL are built.

# What does this allow me to do?

A few things:
 - I am now able to better quantify how much "strain" I am undertaking on an individual ride, or within a week.  Often
times cyclists aim for a certain number of miles, or a certain amount of time on a bike within a given time frame.
The flaw in this approach - not all hours and miles are created equal.  While this approach is far from perfect,
I am now able to **more** accurately quantify the strain I'm sustaining within any given time period.  
- Begin to track trends over time.  Some cyclists or cycling coaches swear by training stress balance and use it
as an "end-all-be-all" metric.  Others discount it completely.  Do I perform better (better meaning lower heart rate
compared to previous similar IF values) when my TSB his higher?  Additionally, I've always perceived my performance
to be better in the morning than in the evenings.  I now can test this with the data I've collected.

I know there are several paid platforms that calculate these things for you, but in order to truly understand 
and interpret these metrics, I wanted to build and implement them myself.  What these platforms don't (usually) offer
is access to the raw data which powers these insights.  I now have both, and have learned a ton along the way!