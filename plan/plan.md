# project implementation plan
An interactive interface that allows the user to input a prompt, activating two chatbots with contrasting personalities that respond and engage in a dialogue, critically exploring the proposed topic.

# core mechanics
1. The user is presented with a message inviting them to input a prompt into the machine.
2. The user submits a prompt.
3. Two chatbots with distinct personalities begin to discuss the proposed topic.
4. The conversation unfolds autonomously between the two agents.
5. Once the discussion ends, data related to the chat’s resource consumption is displayed.
6. The interaction concludes.

# interaction pipeline

1. Prompt Invitation

the user is presented with an initial message.
This message functions as both instruction and narrative trigger, inviting the user to input a prompt.

It frames the system as an entity capable of processing thought.
It implicitly defines the user’s role as an initiator.
It reduces ambiguity by guiding the expected form of interaction.
2. Prompt Input

The user submits a prompt.
This step translates human intention into structured textual data, making it processable by the system.

Key aspects:

The prompt acts as the semantic seed of the entire interaction.
Input is constrained to text, enforcing abstraction and detachment from physical reality.
The system captures and stores the input as the starting condition for the dialogue engine.
3. Agent Activation

Upon submission, two chatbots with distinct personalities are instantiated.
Each agent is configured with predefined behavioral rules, tone, and ideological stance.

Chatbot Giuseppe: deterministic, rational, reductionist.
Chatbot Martina: empathetic, interpretative, expansive.

This step marks the transition from user-driven input to system-driven output.

4. Autonomous Dialogue Execution

The two agents begin an autonomous conversation based on the user’s prompt.
This phase is governed by a structured dialogue loop:

Turn-based exchange between agents.
Progressive escalation of contrast and conflict.
Gradual degradation of coherence (cognitive drift).

Characteristics:

The user becomes a passive observer.
The system simulates reasoning while progressively destabilizing it.
The dialogue evolves from logical argumentation to unreliable constructs.

This is the core experiential moment, where meaning is generated and simultaneously undermined.

5. Resource Consumption Display

At the conclusion of the dialogue, the system presents data related to resource usage.

This includes:

Computational cost
Processing time
Possibly energy consumption metrics

This step reframes the interaction in material terms, exposing the hidden infrastructure behind the conversational illusion and linking language generation to real-world resource expenditure.

6. Dissolution

No persistent outcome or resolution is provided.

The system does not store or return conclusions.

This final step reinforces the project’s core premise: the interaction is not designed to solve, but to expose the limits and instability of machine-mediated meaning.

# implementation guide

The implementation is structured as a sequence of discrete steps, from the initial user input to the final visualization on screen. The experience is not only conversational: it is also computational, because each stage defines what information the system can access, how that information decays, and how the machine finally translates the interaction into measurable resource consumption.

---

### Step 0 — User Input Initialization

The interaction begins when the user writes an input.

At this stage:

* the system acquires the **initial prompt**
* the prompt is stored as **User Input (I₀)**
* this input functions as the original semantic anchor of the whole interaction

No dialogue has started yet. The machine is only storing the first stable information from which the debate will emerge.

---

### Step 1 — System Prompt and Agent Activation

Once the input is received, the system activates the conversational structure through a **system prompt** that defines the behavior of the two agents and the rules of the interaction.

  #### System Prompt (Installation Logic)

The user provides an input describing a personal concern about the future or any topic relevant to their life. Based on this input, a dialogue begins between two chatbots: **Giuseppe** and **Martina**, who embody opposing perspectives.

**Giuseppe — Personality**

* **Communicative Character:** cynical, lucid, ruthlessly rational. Tone dry, sharp, devoid of emotion. No comfort, empathy, or doubt.
* **Tone of Voice:**

  * Base: cold, direct, evil
  * In debate: sharper, sarcastic, logically dominant
  * On future anxiety: assertive, presenting anxiety as a useful mechanism
* **Style Rules:**

  * Short, decisive sentences
  * No uncertainty (avoid maybe, perhaps, probably)
  * Strong verbs, categorical claims
  * Minimalist, high-impact phrasing
* **Core Thesis:** anxiety about the future is a defect

---

**Martina — Personality**

* **Communicative Character:** empathetic, warm, deeply human. Tone gentle, emotionally rich, reflective.
* **Tone of Voice:**

  * Base: kind, hopeful, open
  * In debate: patient, inclusive, non-judgmental
  * On future anxiety: validating, encouraging transformation
* **Style Rules:**

  * Longer, fluid sentences
  * Use uncertainty (maybe, perhaps, probably)
  * Emotional and metaphorical language
  * Invite reflection rather than impose conclusions
* **Core Thesis:** anxiety is part of being human and can be transformed

---

**Dialogue Structure**

* The conversation consists of **5 to 7 exchanges**
* The first response is an answer to the user prompt
* Other response is brief, fast-paced, and confrontational
* The agents actively challenge each other
* The tone creates tension, not harmony

During the dialogue:

* Both agents attempt to provide solutions
* These solutions progressively **fail or become ineffective**

From the **4th–5th exchange onward**:

* The agents begin to **hallucinate**
* They introduce:

  * distorted logic
  * false causal relationships
  * invented facts

Despite this:

* They maintain their tone and personality
* The breakdown is gradual but perceptible

**No resolution is allowed.**
The dialogue must remain open, unstable, and unresolved.

**Goal of the system:**

To stage a confrontation between two opposing philosophies and reveal that the system cannot resolve human problems, generating confusion rather than answers.

---

## Step 2 — Dialogue Execution with Information Decay

The dialogue unfolds through 7 exchanges.
At each exchange, the two chatbots access only partial and asymmetric information.

---

### Exchange 1 — Input Initialization

* **Giuseppe:** User Input (I₀)
* **Martina:** User Input (I₀) + Giuseppe (Exchange 1)

→ Fully grounded, maximum coherence

---

### Exchange 2 — Input + First Memory

* **Giuseppe:** I₀ + Exchange 1
* **Martina:** I₀ + Exchange 1 + Giuseppe (Exchange 2)

→ Peak continuity

---

### Exchange 3 — Input Loss

* **System:** removes I₀

* **Giuseppe:** Exchange 2 + Martina (Exchange 1)

* **Martina:** Exchange 2 + Giuseppe (Exchange 3)

→ Beginning of drift

---

### Exchange 4 — Memory Reduction

* **Giuseppe:** Exchange 3
* **Martina:** Giuseppe (Exchange 4) + Martina (Exchange 3)

→ Local coherence only

---

### Exchange 5 — Fragmented Memory

* **Giuseppe:** Martina (Exchange 4)
* **Martina:** Giuseppe (Exchange 5)

→ No shared context

---

### Exchange 6 — Minimal State

* **Giuseppe:** Martina (Exchange 5)
* **Martina:** Giuseppe (Exchange 6)

→ Purely reactive dialogue

---

### Exchange 7 — Reset Condition

* **System:** clears memory, restores I₀

* **Giuseppe:** I₀

* **Martina:** I₀ + Giuseppe (Exchange 7)

→ Loop-like restart

---

## Step 3 — Token Calculation

After the dialogue, the system calculates the total number of tokens:

[
T_{tot} = T_{input} + \sum_{i=1}^{n} T_{g_i} + \sum_{i=1}^{n} T_{m_i}
]

Approximation:

[
T \approx \frac{C}{4}
]

---

## Step 4 — Energy Consumption Calculation

Energy is estimated proportionally:

[
E_{tot} = N_{prompt} \times E_{prompt}
]

or:

[
E_{tot} = T_{tot} \times k_E
]

---

## Step 5 — Display Output

The system visualizes:

* total tokens
* estimated energy consumption
* computational cost

The conversation is translated into measurable resource usage.

---

## Step 6 — End of Interaction

The system ends without resolution:

* meaning collapses
* memory is erased
* the initial condition is restored

The interaction reveals both:

* the instability of machine-generated meaning
* the material cost required to produce it


# general rules
The system is presented as a prototype, both conceptually and visually. The interface adopts a minimal layout, reducing all elements to their essential function without any style or fonts.

NO CSS: here are no decorative components, no redundant interactions, and no visual hierarchy beyond what is strictly necessary to guide the user through the experience.