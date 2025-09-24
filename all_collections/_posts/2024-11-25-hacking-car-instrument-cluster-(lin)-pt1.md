---
layout: post
title: Hacking Car Instrument Cluster (LIN) PT.1
date: 2024-11-25 10:38
categories: ["automotive", "hacking", "embedded"]
---

The time has come to address the elephant, or rather a set of automotive junk, in the (living) room.
...and to encourage you to keep reading, here's the current state of said room:

![Setup](<../../assets/posts/hacking-car-instrument-cluster-(lin)-pt1/setup.jpg>)

_Note: I’m lucky my girlfriend doesn’t care much about this._

## Backstory

---

### The Past

In the past, I played with car instrument clusters. My first project was a [Golf Mk.3](<https://en.wikipedia.org/wiki/Volkswagen_Golf#Third_generation_(Mk3/A3,_Typ_1H/1E/1V;_1991)>) based shelf clock, and I even made a video about it.

<iframe width="560" height="315" src="https://www.youtube.com/embed/3B7vaYgUk3w?si=xsYxFtgzYmxU3zc4" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

That project was, however, ridiculously easy. It only required supplying a [PWM signal](https://botland.store/blog/pwm-signal-what-is-it/) directly from an Arduino, no signal amplification was needed. Feeling more ambitious, I moved on to a [CAN](https://www.csselectronics.com/pages/can-bus-simple-intro-tutorial)-based cluster from a [Jaguar X-Type](https://pl.wikipedia.org/wiki/Jaguar_X-Type) and made a video about that too.

<iframe width="560" height="315" src="https://www.youtube.com/embed/XNLJWUMKByM?si=85ZGuxg1ZmkZlKqS" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

I consider that attempt cheating, though. I connected a CAN bus adapter, received a few frames, and quickly realized I’d probably need the car (a Jag) to figure out what’s actually "flying" around in the CAN bus. CAN frames aren’t universal, not all of them, at least. Each manufacturer defines their own set of rules (IDs, data streams, etc.). The best way to crack these rules for a specific car model is to plug in a CAN adapter and observe the network activity.

In the end, I just hacked directly into the motors and got them moving with an Arduino.

### The Not-So-Distant Past

While browsing YouTube, I stumbled upon this video:

<iframe width="560" height="315" src="https://www.youtube.com/embed/7uGUtiS9Tww?si=-UHIeKXrjmU_CVAj" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

The author demonstrated that even without knowing the CAN bus rules for a specific car, it’s still possible to reverse-engineer CAN frames. The technique involves spamming the cluster with common data patterns (e.g., all 0s, all 1s, alternating 1s and 0s like `0x55`, etc.) across the entire ID range and observing how the cluster reacts.

After watching this, I thought: _"Why didn’t I think of that back then?"_

And with that inspiration, I headed over to Allegro (the Polish equivalent of eBay) to look for an Alfa Romeo 159 auxiliary instrument cluster. Why? Initially, I wanted to integrate it into my car, thinking it might fit (spoiler: not a chance). My car lacks a coolant temperature gauge and a turbo gauge, and I thought it would be quite an accomplishment to integrate a cluster from a completely different car (model and manufacturer) into mine.

## Hacking the Cluster - Attempt I

---

Rather than starting with where I’m at now, let me take you through what I attempted in chronological order. Spoiler: it didn’t go according to plan.

### Overly Optimistic

I bought the cluster for 30zł (~$7) with shipping. It wasn’t in the best condition, 60% of the tabs holding the front clear panel in place were broken.

![Broken tabs](<../../assets/posts/hacking-car-instrument-cluster-(lin)-pt1/broken-tabs.jpg>)

I disassembled the cluster to clean it and check what ICs were used. I was almost certain the cluster relied on CAN bus to communicate, though the [service manual for the Alfa Romeo 159](https://aftersales.fiat.com/elearnsections/main.aspx?nodeID=939003534&languageID=2&modelID=939000000&valID=939000001&prodID=939000002&markID=2&dhb=INSTRUMENT%20PANEL%20-%20DESCRIPTION&modelName=Alfa%20-%20140%20-%20Alfa%20159&langDesc=English&sectionName=Impianto%20Elettrico&validityName=2.4%20JTD%2020V) mentioned:

> The centre module is not a B-CAN node, but is connected by means of a special serial line to the instrument panel node which sends the module all the signals necessary for the display of the required information.

At the time, I assumed they just didn’t want to share what protocol was used, so I rolled with the idea that it was CAN. It all made sense to me. The auxiliary cluster (as the manual calls it) has only four wires. I figured these must be VCC, GND, CAN HIGH, and CAN LOW. I also checked whether the main IC had an integrated CAN bus controller, and it does. So, it _had_ to be CAN, right?

![Wires and IC](<../../assets/posts/hacking-car-instrument-cluster-(lin)-pt1/wires_and_ic.jpg>)

### Connecting the Cluster to the PC

To send data frames to the cluster, I bought a [CANable v1.0](https://canable.io/), a USB CAN debugger/adapter. I chose this one because it was cheap and supported natively by [Linux can-utils](https://github.com/linux-can/can-utils), meaning I wouldn’t need any extra software, just the way I like it.

Once the debugger arrived, the only thing left was to power the cluster. I initially used a bench power supply, but I quickly got tired of dealing with cables sticking out of the cabinet. So, I figured... why not create a more _cursed_, yet (in my opinion) elegant solution?

![Le power bay](<../../assets/posts/hacking-car-instrument-cluster-(lin)-pt1/power_bay.jpg>)

What you’re looking at is a [3.5" bay banana socket frontplate adapter](https://www.thingiverse.com/thing:6759175) I designed. The banana sockets are connected to my PC’s internal power supply to provide 12V (the same voltage level cars operate on) to the cluster. I harvested some old SATA extension cables to make it, so don’t worry, it’s not hard-wired.

### I Did Something Stupid

I connected the cluster to the adapter, supplied power, and hooked everything up to the PC. Everything seemed fine. I installed the necessary packages, learned a bit about using CAN on Linux, and wrote some bash scripts to spam the cluster with data frames across the full ID range, just like the author in the video I mentioned earlier.

And... nothing.

No matter what I tried, I couldn’t receive anything from the cluster (assuming it sends any data), nor could I make it respond. Something, however, made me double-check the connections with a multimeter. That’s when I discovered the problem: for some reason, the supposedly CAN lines were at 12V.

#### Why Is That Bad?

Well, CAN [operates at less than 5V](https://www.ti.com/document-viewer/lit/html/SSZTCN3) and I just somehow, inadvertently sent 12V pulses to the USB port. Luckily, the PC still works, though I'm not so sure about the state of the CAN adapter. Honestly, I’d rather lose a 35zł adapter than my year-old PC, but still I admit that was a stupid thing to do!

### The Mystery of 12V

If I recall correctly, the first thing I did after this "incident" was ask ChatGPT about other automotive buses that operate at 12V. The answer? [**LIN - Local Interconnect Network**](https://www.csselectronics.com/pages/lin-bus-protocol-intro-basics).

I disassembled the cluster again, and this time, I found it: the LIN transceiver. How did I miss it the first time? Well, it’s the only IC located on the front side of the PCB, somewhere in the marked area:

![LIN IC location](<../../assets/posts/hacking-car-instrument-cluster-(lin)-pt1/lin-ic-location.jpg>)

I hadn’t removed the needles or the gauge background assembly initially because I assumed the engineers would’ve used the main IC’s CAN support.

Later, I confirmed the auxiliary cluster uses LIN by analyzing wiring diagrams. [This diagram](https://4cardata.info/elearn/939/2/939000002/939000003/939000003/939011715) showed that the auxiliary panel connects to the main panel, and the [main panel’s pinout diagram](https://www.manualslib.com/manual/1110450/Alfa-Romeo-159.html?page=272#manual) clearly states `LIN bus`.

### Oh, the Misery...

And that’s how what should’ve been a straightforward automotive instrument cluster hacking project turned into a challenge to get it working _at all costs_.

## Hacking the Cluster - Attempt II

---

After discovering that the cluster operates on a LIN network, I had to come up with a new plan.

### Obtaining a LIN Bus Adapter

Affordable LIN bus adapters are practically nonexistent. The options are either professional debugging kits that cost thousands or sketchy Aliexpress adapters, which require downloading software from some mysterious Chinese server (foreshadowing) and learning Mandarin to make them work.

However, there was one promising option: the [LIN USB Converter (LUC) by UCANDEVICES](https://ucandevices.github.io/ulc.html).

LUC is an open-source product developed by a Polish guy. This is both a good and bad thing. Good, because it’s open-source (FREEDOM!) and can be adapted to specific needs. Bad, because based on my experience, when the programmer and the reviewer are the same person, the code quality can be... questionable. My doubts grew as I watched demonstration videos, read the webpage, and skimmed through the "documentation". None of it exactly screamed "quality".

Still, my options were limited: either an open-source product I could modify if necessary, or a completely proprietary device that required downloading random files from a Chinese server. The professional adapters were simply out of my budget.

So, I pulled the trigger and bought the LUC adapter. It cost me 131zł (~$32) with shipping.

### The Setup

Since my setup was already prepared, installing the LUC was just a matter of swapping out the CANable for it. According to the LUC’s [documentation](https://ucandevices.github.io/ulc.html), it should work with Linux can-utils:

> SLCAN compatible, works with LINUX socket-can and some of CAN-utils.

However, I'm yet to find documentation on how to actually set it up with Linux (bruh).

The simplest solution at the time was to use the dedicated software for LUC called [uCCBViewer](https://github.com/UsbCANConverter-UCCbasic/uCCBViewer), also developed by the same guy.

The problem? uCCBViewer is a GUI-based app, and my PC/server doesn’t have a GPU. Luckily, this wasn’t a dealbreaker. With the help of the [VNC protocol](https://discover.realvnc.com/what-is-vnc-remote-access-technology), I was able to render graphics on the client machine. After some setup, I could access the GNOME desktop of my server on my MacBook.

If I were to do this today, though, I’d probably just set up a separate VM instead of installing it directly on my server.

### Here We Go Again

With the setup ready, I tried the same trick I used for CAN: spamming IDs with data. Since [LIN only supports 64 IDs](https://www.csselectronics.com/pages/lin-bus-protocol-intro-basics), compared to CAN’s [11-bit addresses](https://tractorhacking.github.io/IdExplanation/), it’s much simpler. I could manually check each ID without needing to automate anything.

But once again, no matter what I tried, nothing happened on the cluster. It didn’t respond to my attempts, and I didn’t receive any data from it either.

## Hacking the Cluster -- Attempt III

---

The previous attempt was pretty discouraging, but I’ve already put so much effort into this project that there’s no way I’m giving up halfway through.

### There Were Two Clusters, Right?

In the first picture of this blog post, you might have noticed two clusters. Here’s a close-up:

![Both clusters](<../../assets/posts/hacking-car-instrument-cluster-(lin)-pt1/both_clusters.jpg>)

You probably see where I’m going with this. I decided to buy the main instrument cluster (the one on the bottom) as well. As I mentioned earlier, the auxiliary cluster (on top) is controlled by the main cluster. This means that if I connect the two, I should see some kind of activity on the bus.

### Custom PCB

Now that I have both clusters, here’s what I need to do:

- Supply power to both clusters.
- Connect their data lines.
- Plug the LUC adapter in the middle to monitor the bus activity.
- Connect a probe to check for bus signals.
- Leave room for a CAN adapter in case I want to send data to the main cluster to control the auxiliary one later.
- Include a way to unplug one of the clusters to avoid ID collisions when I start sending my own frames.

If this sounds like a recipe for wire spaghetti, you’re absolutely right. And the last thing I need is a mess of dodgy connectors.

To keep things clean, I designed a custom PCB to handle everything on that list.

![PCB and Oscilloscope](<../../assets/posts/hacking-car-instrument-cluster-(lin)-pt1/pcb.jpg>)

There’s nothing fancy about this PCB. It just handles all the necessary connections, probe points, and switches. I’m showing it here to emphasize how committed I am to this project. I even had the PCBs made by a popular PCB manufacturer. Since the minimum order quantity was five, I still have a few spares. If anyone’s interested in buying one, hit me up!

#### Oscilloscope

In the corner of the picture, you’ll notice I’ve hooked up an "oscilloscope." Now, let’s be clear, this ain't the most precise piece of equipment in the world, but any oscilloscope is better than no oscilloscope. While I can’t use it to physically decode signals (that is a way of doing it), it at least confirms there’s activity on the bus.

### A Gleam of Hope

Finally, with everything set up, I could see activity on both the oscilloscope and in the uCCBViewer software. The auxiliary cluster even sprang to life, illuminating the gauges.

![No data](<../../assets/posts/hacking-car-instrument-cluster-(lin)-pt1/no_data.jpg>)

But it’s not all sunshine and rainbows. Sure, I can see activity, but there’s a problem. While I see the IDs, I don’t see any data. And I’m pretty sure I _should_ see something.

## Hacking the Cluster -- Attempt 3.5

---

I don’t consider this a full attempt. At this point, I just needed to prove to myself that I wasn’t descending into madness.

### What Am I Even Talking About?

The auxiliary instrument cluster has two data lines:

- **LIN Bus**
- **Dimmed positive lighting command from the instrument panel**
  ([as described in the service manual](https://aftersales.fiat.com/elearnsections/main.aspx?nodeID=939003534&languageID=2&modelID=939000000&valID=939000001&prodID=939000002&markID=2&dhb=INSTRUMENT%20PANEL%20-%20DESCRIPTION&modelName=Alfa%20-%20140%20-%20Alfa%20159&langDesc=English&sectionName=Impianto%20Elettrico&validityName=2.4%20JTD%2020V)).

I confirmed that I don’t need the second line for the cluster to illuminate, which means _some_ data is definitely flowing on the LIN bus. I just can’t see it.

### Proving the Theory

To prove my theory, I needed to get the main cluster to drive the auxiliary cluster. I connected the CAN adapter to the main cluster and tried spoofing CAN frames, as I did before, but with no success. At this point, I wasn’t sure if I was doing something wrong, if the adapter had been fried during "the incident", or if it never worked to begin with.

Then I noticed something interesting in the [main cluster pinout manual](https://www.manualslib.com/manual/1110450/Alfa-Romeo-159.html?page=272#manual). There’s a pin labeled:

> Supercharger pressure signal (PWM)

As luck would have it, the boost pressure gauge is on the auxiliary cluster. And since I can generate a PWM signal with almost anything, this was worth a shot.

![Arduino](<../../assets/posts/hacking-car-instrument-cluster-(lin)-pt1/arduino.jpg>)

One Arduino later, and _it’s confirmed!_ The data must indeed be flowing on the LIN bus. Unfortunately, it also confirms that the LUC and its software combo are not able to display that data. But hey, the turbo pressure gauge works!

![Turbo](<../../assets/posts/hacking-car-instrument-cluster-(lin)-pt1/turbo.jpg>)

...but where does that leave me?

## Hacking the Cluster - Attempt IV

---

For this attempt, I wanted to see if the issue was due to a mismatched baud rate. Perhaps my cluster was using a non-standard rate, and that’s why I was seeing garbage data.

### Action Recompilation

How do I even start explaining this…? Out of the box, the LUC firmware supports two baud rates: **19200** and **9600**. Later, I discovered hidden firmware releases in the [LUC GitHub repository](https://github.com/uCAN-LIN/LinUSBConverter/releases). Among these, version 2.0 **HAD** (emphasis on _had_, because it was removed in later versions) support for custom speeds. However, this feature was implemented with a different parameter than the two base speeds, and the GUI app still had only the default rates hardcoded. So, yeah… I can't make sense of it either.

To work around this without rewriting the GUI app, I needed to modify the LUC firmware. The idea was to set the custom baud rate directly in the firmware code, so that when I selected **9600** baud in the app, the adapter would actually operate at my specified custom speed.

### The Quest for Firmware Customization

And thus began the saga.

First, I wrestled with an outdated STM32 IDE (so bad, I don’t even want to remember its name) because that’s what the README suggested. When that proved impossible, I switched to a newer IDE that at least had a functioning toolchain and preserved settings. Progress!

But of course, more problems arose. There was no way the code on the master branch could compile without modification. I used Git to roll back to earlier versions, hoping to find a working state. Still nothing. I couldn’t understand how anyone ever got this thing to compile, it felt like I was deciphering lost runes.

Then came the missing submodules. For reasons unknown, they wouldn’t fetch properly, so I had to download them manually like some kind of animal. Naturally, the submodules included unnecessary files, which I had to clean up to avoid further errors.

I spent hours poring over comments, pull requests, and GitHub issues left behind by my ancestors who had also attempted to tame this cursed codebase. Their struggles were eerily familiar.

What should have been a half-hour task took **multiple evenings** of frustration. But in the end, I managed to compile the firmware. Victory?

### But of Course, There’s a Catch

Even with the firmware compiled, the GUI app behaved bizarrely. To avoid freezing everything, I had to select **9600 baud** first in the app, otherwise it and the LUC locked up. This quirk wasn’t limited to my compiled firmware; it happened with the official GitHub releases as well. Why? I don’t know. At this point, I didn’t even want to know. I wasted another evening assuming my compiled firmwares were corrupted before realizing it was just another “feature.” Fantastic.

### Ok, But Seriously...

_Breathe in… Breathe out…_

Did I manage to see any data frames? **No.**

I recompiled the firmware with various baud rates, none worked. My frustration reached the point where I seriously considered building my own LIN adapter from scratch rather than continuing to wrestle with the LUC.

If I want to create a standalone device using this cluster, I’ll need to develop my own solution anyway. But first, I need to figure out what the LIN bus frames actually look like. Until then, I’m stuck.

## Summing it Up

---

In the end, I did not manage to control the auxiliary instrument cluster of the Alfa Romeo 159, but I do not announce defeat yet! Here's a little sneak peek of what's to come in part II, and if you read carefully, you know what kind of cursed adventures await me with this.

![Foreshadowing](<../../assets/posts/hacking-car-instrument-cluster-(lin)-pt1/foreshadowing.jpg>)

I was hoping I could release this journey as a single YouTube video, but as you can see, it looks like everything is against me on this project. I had to just get it out of my head "on paper" so I could make space in my brain for new things and continue this project. Part two is coming, one way or another.

Looking back at it, the real progress I made on this is next to none, but I know I already learned a few things along the way, and there is still much to come.
That's why I don't feel like this time was wasted, nor am I discouraged. I know that failures are the most valuable lessons, even though I think my failure on this one comes from a limited toolset. I also believe that even if I don't have a working solution, I at least have this post to share, and who knows, maybe it'll help me one way or another in the future.

## Links

---

This is mostly for future me, but if you're interested in messing with the Alfa Romeo 159 cluster yourself, here are some links that might be helpful:

- [Alfa Romeo 159 instruments](https://aftersales.fiat.com/elearnsections/main.aspx?nodeID=939003534&languageID=2&modelID=939000000&valID=939000001&prodID=939000002&markID=2&dhb=INSTRUMENT%20PANEL%20-%20DESCRIPTION&modelName=Alfa%20-%20140%20-%20Alfa%20159&langDesc=English&sectionName=Impianto%20Elettrico&validityName=2.4%20JTD%2020V)
- [Alfa Romeo 159 Training Material - Auxiliary Instrument Panel](https://www.manualslib.com/manual/1110450/Alfa-Romeo-159.html?page=268#manual)
- [Alfa Romeo Training Manual - Main Panel Pinout](https://www.manualslib.com/manual/1110450/Alfa-Romeo-159.html?page=272#manual)
- [Instrument Panel Wiring Diagram](https://4cardata.info/elearn/939/2/939000002/939000003/939000003/939011715)
- [Wire Color Codes](https://4cardata.info/elearn/939/2/939000002/939000003/939000003/939011858)
