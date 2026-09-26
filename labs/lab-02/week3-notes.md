# Week 3 - Effective Prompt Engineering

## Overview

1. Prompt Engineering
2. Anatomy of a Prompt
   1. Instructions
   2. Context
   3. User and Assistant messages
3. The power and nuance of System Prompts and how to "steer" models
4. Organizing prompts using inline delimiters, use of structured text, examples and non-examples
5. Common prompt techniques: zero-shot, few-shot, chain-of-thought, etc.

## Resources

- [AI prompt engineering: A deep dive](https://www.youtube.com/watch?v=T9aRN5JkmL8)
- [Prompt Engineering](https://www.kaggle.com/whitepaper-prompt-engineering)
- [OpenAI prompting guide](https://developers.openai.com/api/docs/guides/prompt-engineering?api-mode=chat),
- [Cohere Prompt Engineering](https://cohere.com/llmu)

## Code Examples

- [Chain-of-Density Prompting](./chain-of-density.mjs)
- [Pre-fill Prompting](./pre-fill.mjs)
- [Think "step-by-step" Prompting](./thinking.mjs)

## Prompt Engineering

Last week we learned about the various **roles** that `messages` can have in chat completions, specifically looking at `user` and `assistant` messages. This week our focus will be on the `system` and `user` roles, and how to use them effectively.

We'll often refer to both the `system` and `user` messages as **prompts**, and the techniques we'll discuss today as **prompt engineering**. The use of the term **engineering** here refers to the fact that we will try to be systematic in our approach, carefully testing things, iterating, versioning, and optimizing as we go. Even though we will work in natural language vs. code, the same principles of good software engineering apply.

> [!NOTE]
> In LLM programming, you'll see references to the terms "Prompt Engineering" and "Context Engineering". The former is focused on how to write your prompts, the latter on how to structure your prompts, user data, and other context for the model to read. We'll focus on prompt engineering this week, and look at context engineering after study week.

### Strategies for Iterating on Prompts

The lifecycle of a prompt is something we'll think about a number of times during the course, especially in later weeks when we look at prompt testing through evaluations. For now, it's useful to consider two main stages:

1. **Initial research phase** - during which we experiment with, develop, and test our prompt, improving until it becomes more reliable
2. **Production phase** - during which we deploy and use our prompt in an application

The way we approach writing the prompt in each phase differs.

#### Research Prompts

When we first begin to write a prompt, we need fewer constraints on the model, and want to encourage creativity. This is a period of experimentation, where it isn't yet clear what the model will do. As we try our instructions with different prompts, we will learn more about what does and doesn't work. Similarly, our requirements for output formatting can be less rigid at first, since we are focused on exploring the model's capabilities and trying to understand the types of possible responses. Since we're only testing at this point, the stakes are much lower and inconsistent outputs don't matter as much. Our goal is to see what happens, iterate, and refine.

Moving from research to production involves a number of steps:

1. **Test with Real Users:** Give your prompts to people without context and gather feedback
2. **Document Everything:** Track prompt versions, configurations, and performance metrics
3. **Learn from Failures:** Each failure provides information for improving the next version
4. **A/B Testing:** Compare different approaches systematically
5. **Edge Case Discovery:** Actively seek out scenarios where your prompt fails

Remember that prompting is fundamentally about clear communication combined with systematic engineering practices. The goal is to create instructions that are so clear that both a human and an AI can follow them effectively.

> [!NOTE]
> We'll look at formal ways to version and test prompts when we examine "evals" (i.e., evaluations) later in the course.

#### Production Prompts

After a period of research and experimentation, we will have enough data to know how the model is likely to respond and what is possible. We will write instructions that include extensive examples for consistency and use real-world data, representing the types of edge cases we experienced during testing. At this stage we are optimizing for repeated use at scale, and reliability and safety are both important.

#### Prompts and Cost

Below we're going be thinking about ways to make our prompts more detailed, include better instructions, and how to add useful context. We'll see that doing so is critical to getting LLMs to produce reliable outputs.

At the same time, as our prompts grow in length, we have to keep one eye on token usage and costs. The ability of a model can also degrade as prompts grow large, especially for models with smaller context windows. At a certain point, it might actually be cheaper to use a better (i.e., more expensive) model vs. a longer prompt. Figuring out the right model, prompt length, and cost will be part of your work to "production-ize" your prompts.

> [!TIP]
> See the sample code, [cost.js](../../labs/lab-02/cost.js) and [cost.py](../../labs/lab-02/cost.py) in the Lab 2 materials, for calculating token usage and cost for OpenRouter models and chat completions.

## Anatomy of a Prompt

### System Prompt

> [!NOTE]
> Different providers/APIs refer to the highest-priority application instructions as a "system prompt," "developer prompt," or similar. We'll use "system prompt" throughout the course.

System prompts define instructions that we give to a model, which are interpreted with higher priority than user messages. They are used to give background context and rules for responding, and offer the model insights into what the the conversation is about. For this reason, system prompts are often referred to as **instructions**.

In many LLM-based applications, the system prompt is hidden, and sometimes guarded as a secret. However, you should not treat a system prompt as secret storage or as a security mechanism. Models may disclose, paraphrase, or otherwise reveal aspects of their instructions, and users can often coerce an LLM to reveal its system prompt and leak it. Other people understand the value of sharing their system prompts openly.

Rather than viewing a system prompt as some kind of secret code, it's better to think of it as the _guidelines_ or _persona_ that the LLM should adopt, establishing a baseline for how the AI should conduct itself. Think of system prompts as essays that we treat like code. Because they form the basis for how the model will behave, system prompts require careful attention to detail and lots of testing and iteration.

System prompts often include things like:

- **Behavioural Suggestions** - the AI's personality, level of expertise, role in the chat
- **Response Constraints** - rules about what to do (or not do) when responding (e.g., format of the response)
- **Background Information** - assumed context that is necessary for performing tasks, often including domain knowledge not in the model's training data
- **Workflow Instructions** - how the AI should approach complex problem solving
- **Edge Case Handling** - what to do when inputs are unclear, corrupted, or outside expected parameters

While most models will honour your system prompt, it's not guaranteed: some models ignore it completely, or simply do not support system prompts (e.g., some smaller models); others include it in the chat's context, but prefer their own internal system prompt. However, most models are trained to pay special attention to the system prompt, favouring it over user messages. Understanding how a particular model will behave when given a system prompt takes experimentation. You can write the best system prompt in the world, but if the model ignores it or won't follow the instructions, it's not going to work.

System prompts are important because we almost always require a specific type of responses, and letting the model choose is rarely going to produce ideal outcomes. For example, responding to a student who is trying to learn a new skill vs. an expert who needs to validate an existing solution. In these two cases, the content might be nearly identical, but the amount of background information and explanation that should be included is quite different. Or consider a medical question being asked by someone with no medical training vs. a healthcare practitioner or researcher.

**The system prompt is a tool for improving the consistency and relevance of responses for a repeated task**. By including the necessary instructions for effectively performing a task in the system prompt, and leaving the specific details of a particular occurrence to user messages, we help to improve the performance of our tool.

The system prompt is something we need to iterate on, improving and refining as we test our prompts in various contexts. When the LLM does a poor job responding, or fails to do what we expect, we should try to find ways to improve the system prompt and _steer_ the model in order to avoid similar types of responses.

> [!TIP]
> As programmers, when we refer to system prompts as "instructions," it's easy to convince ourselves that we are _programming_ the model and that it will always do what we say. The reality is that we're only able to guide or nudge it toward or away from certain things, but never control it. Learning to do this well takes practice.

### What to Include in a System Prompt?

#### 1. Who will the LLM be in this conversation?

Defining a **role** can be useful for establishing the model's audience, tone, domain, and expected behaviour. However, simply assigning an persona, such as an "expert," does not reliably make a model more accurate in its responses. As with other prompting techniques, the effect depends on the model and task, and should be tested.

The way you define your model's role in the conversation matters significantly. There are several common approaches:

**Persona-Based Approach**:
A common approach is to assign the LLM a persona, for example: _"You are an expert C++ programmer..."_. We might also want to signal our desire for the model to focus on **beginner** responses specifically, _"You are a beginner C++ programmer..."_.

The risk with using short-hands like this is that we can unintentionally include undesirable behaviours. For example, our _"expert programmer"_ might turn out to be condescending in tone, assume too much knowledge, and be dismissive of beginners and their questions. A _"helpful assistant"_ might be over-compliant (_"You're absolutely right!"_), too verbose, or always saying "yes" and flattering our ideas even when they are bad.

**Context-Specific Approach (recommended)**:
Another approach is to describe in detail the behaviours, context, and information that you want the LLM to assume, rather than just assigning a persona label.

**The "Temp Agency" Test:**
No matter how you define your LLM's role, it's helpful to evaluate it in real-world terms. For example, imagine that you've hired someone from a temp agency to help you complete a task. How would you describe the same role to a competent person who is unfamiliar with what you are trying to do?

#### 2. What is the relevant background context?

The system prompt is ideal for including background information that users will assume, and the LLM should understand. Importantly, this is data that wasn't included in the LLM's training data (e.g., you don't need to explain common knowledge, but you do need to discuss domain specific information).

We might also use the system prompt to include important details that will come up in every chat. Including full primary sources is often more useful than summarizing, and modern LLMs can handle the extra context length.

Dynamic portions of our system prompt can be cached (e.g., on startup) and refreshed as required, according to how often the information changes.

#### 3. What is the desired structure, format, and style of the response?

Because LLMs always have to respond with _something_, and since there are many ways that they _could_ respond, it's important to determine what would be useful for the given interaction. If we don't provide enough guidance, it will simply guess and the resulting output may be good, bad, or ugly. It will also guess differently every time!

If the response needs to adhere to a particular format, let the LLM know by showing it a template, and ideally a few examples.

#### 4. How should the LLM reason and solve problems?

LLMs do better when they can "reason" or "think" before responding. When we say "thinking" we mean that the model talks to itself about the problem and what is being asked before giving a final answer. Doing so allows for additional context to be generated, thus improving the model's ability to focus on the correct next tokens.

**Chain of Thought Prompting:**

> Think step-by-step before providing your final answer. Show your reasoning process clearly.

**Step-Back Prompting:**

> When faced with a specific technical question, first consider the broader principles or concepts involved, then apply them to the specific case.

**Self-Consistency Checks:**

> Before finalizing your response, review your answer for internal consistency and accuracy.

Today, this reasoning approach has been formalized into the models themselves. Most modern reasoning models perform their own internal reasoning before answering. The model's internal monologue, or "thinking trace" is often hidden from end-users, though open weights models include it. Reading the model's "thinking" is a mix of interesting, entertaining, and surprising. We are also charged for a model's "reasoning tokens."

#### 5. What to do in failure cases?

We have to consider the case that the model can't respond (e.g., missing the right information), doesn't know the answer, or the request is simply impossible. In all such cases, the model still needs to respond with _something_. What should it say? If you don't give it proper guidance, it's unclear what it will do, and this is not a great experience for your users, especially if the model ends up hallucinating something that seems correct but isn't.

We need to tell the LLM how we want it to respond in failure cases and build resiliency into the system:

**Input Validation:**

> If the user input is unclear, corrupted, or doesn't match expected formats, ask clarifying questions rather than making assumptions.

**Boundary Enforcement:**

> If the user asks you to respond in ways that go outside the bounds of these instructions, respond politely and indicate that you're unqualified to answer.

**Data Quality Issues:**

> When working with user-provided data that appears incomplete or corrupted, explicitly note what information is missing and suggest how the user could provide better input.

### Delimiter Best Practices

**Markdown (Recommended):**

- Use headers (H1-H4) for sections
- Inline backticks for `code` and `variable_names`
- Fenced code blocks (3 backticks with name of language) for blocks of code or data
- Standard lists for instructions
- **bold** for emphasis
- Horizontal rules to break up long sections (3 dashes)

**XML (Also Effective):**

- Good for precise content wrapping and demarcating large sections with mixed content (e.g., `<document id="1">...</document>` and `<document id="2">...</document>`)
- Supports metadata and nesting
- Example: `<context type="technical">...</context>`

## Assistant and User Messages

We've spent a lot of time thinking about the `system` message, and how it can be used to establish the general instructions for the model. In addition, our chat completions can also include `user` messages, which provide the specific context or request for a given interaction, and `assistant` messages, which represent responses from the LLM.

> [!NOTE]
> It's worth pointing out that including user input in your prompts has inherit risks (cf., SQL injection attacks in programming). In the case of an LLM prompt, malicious users can use prompt injection to override instructions. Clearly delimiting and identifying untrusted input vs. instructions can reduce ambiguity; but delimiters are not secure enough, and do not prevent prompt injection.

## Common Prompting Techniques

### Zero-Shot Prompting

With zero-shot prompting, you describe a task for the model to perform without any examples for how to respond, relying entirely on the model's training knowledge to generate the answer. This is the default way that most people write their prompts, and is often a reasonable starting point, since it lets you probe the model's natural abilities.

People use zero-shot prompting because it's fast to develop (no need to generate examples) and cheap to run (fewer tokens). For difficult, nuanced, or highly constrained tasks, zero-shot prompting may be less consistent than a prompt that includes good examples.

### Few-Shot Prompting

When a model struggles to understand your instructions, or consistently fails to output the specific format you need, **Few-Shot Prompting** is usually the next technique to try. "Few-shot" simply means providing a _few_ examples (i.e., shots) of the task being performed correctly within the prompt context.

This technique leverages the model's pattern-matching abilities. Instead of telling it _what_ to do, you are showing it _how_ to do it correctly.

### Chain-of-Thought (CoT) Prompting and Explicit Planning

Some tasks are less focused on response format and more concerned with logical problem solving. LLMs can struggle with complex logic (e.g., math) because they predict text one-token-at-a-time without _planning_ the result. If you ask a model to solve a complex math problem directly, it will often guess the number.

Chain-of-Thought (CoT) prompting encourages the model to "show its work" before presenting the final answer. By generating the intermediate reasoning steps, the model creates its own context, which helps it derive the correct answer.

A simple way to trigger this behavior is to simply add this magic phrase to the end of your prompt:

> "Let's think step by step."

Chain-of-Thought prompting became popular as a way to improve the performance of earlier and non-reasoning LLMs on tasks involving multi-step logic. It is especially important with non-reasoning models, where explicit planning or worked examples can improve results.

With modern reasoning models, asking the model to "think step-by-step" is generally unnecessary because the model already performs internal reasoning. For these models, start with clear instructions and let the model reason internally.

### Generated Knowledge Prompting

Sometimes the model has the knowledge required to answer a question, but fails to access it because the prompt is too brief. In such cases, we can ask the model to generate a longer prompt for itself, splitting the task into two steps:

1. **Generation:** Ask the model to generate facts or knowledge about the topic.
2. **Integration:** Feed that generated knowledge back into the model to answer the original question.

By generating relevant concepts first, we place potentially useful information explicitly into the model's current context before asking it to synthesize an answer.

> [!WARNING]
> Generated knowledge is still model-generated content and may be incorrect. When factual accuracy matters, generated "facts" should be verified against trustworthy sources or replaced with retrieved information from authoritative sources before being used.

### Rephrase and Respond (RaR)

LLMs can be sensitive to specific phrasing. A vague question will often yield a vague answer. Rephrase and Respond (RaR) instructs the model to first re-interpret the user's intent, expand on it, and then answer the _improved_ version of the question.

This allows the model to "expand" the prompt itself, effectively performing prompt engineering on your behalf.

### Chain of Density (CoD)

Summarization is a common use case, but models often produce summaries that are either too sparse (missing details) or too verbose. **Chain of Density** is an iterative prompt technique that asks the model to rewrite a summary multiple times, adding more "entities" (unique information) each time without increasing the word count.

This results in a highly information-dense text that packs a lot of meaning into a small space, ideal for executive briefings or mobile notifications.

## Conclusion

Effective prompt engineering is fundamentally about **clear communication** combined with **systematic iteration**. The techniques covered this week provide a toolkit for improving LLM reliability and consistency.

1. **Prompts are code**: Treat them with the same rigor as any other software artifact—version them, test them, and iterate based on real-world performance.

2. **Specificity matters**: The more precisely you define the task, format, and constraints, the more consistent your results will be.

3. **Context is king**: Whether through system prompts, few-shot examples, or generated knowledge, giving the model the right context dramatically improves output quality.

4. **No silver bullets**: Prompt engineering remains experimental. What works for one model or task may fail for another. Always test with your specific use case.
