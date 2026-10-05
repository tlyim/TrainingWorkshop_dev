Clarification on the purpose of the Jupyter notebook 


Dear Robbie,

Sorry to know that you ran into various issues. Please see if my replies below help.

>> Claude is suggesting that this will limit my ability to save and that I should create a new code space and delete the old one.

Given that it might take longer than expected for you to go through the preliminary materials, I think you should just work with the Codespace directly created from the Workshop repo. You can still save changes to the Jupyter notebook within the Codespace — you just can't save changes persistently back to the Workshop repo of which you are not the owner. This last part is not critical at this stage. 

>> I have looked at the notebook Prelim2_Jupyter_PythonBasics but the instructions are quite confusing and I can’t fully understand what the activity itself is.

The Jupyter notebook introduces to you the fundamental concepts of the data types in Python. Code works with data, and different types of data have different expected behavior and have to be handled differently. After learning the concepts illustrated with the simple code in each cell of the notebook, hopefully you are able to tell how '12' is different from 12  and from 12.0 in Python. For example, if you have two datasets one indexed by a column of ID stored in string (e.g., '987654') but the other indexed by a column of ID stored in integer (e.g., 987654), then you know you must first turn the string type data into integer type (or the other way around) before you can merge them to identify records linked by the same ID. 

>> Is completing this required before the session? Because I am struggling to get to grips with it at current and understand what it is I am meant to be learning.

Different students have different backgrounds and might find some learning approach more effective than another. Based on your response, I recommend you to try the below. 

Assuming you have a free/paid ChatGPT/Claude/Gemini/Owen/Grok account. Upload the Jupyter notebook to the account and ask: "What does this Jupyter notebook try to teach a learner?"
Next, from the beginning to the end of the notebook, copy every three pairs of the Markdown and Code cells to the AI account and ask: "What do these several pairs of Markdown/Code cells try to teach a learner?"
As you proceed, if you find the output of a code cell puzzling and unexpected, copy the code cell to the AI account and ask: "I thought the outcome of the code cell should be such and such, however, it isn't like that. What am I missing?"
Another question you can always ask AI: "What is the practical usefulness of understanding what these several code cells try to teach a learner? Give me a concrete example for illustration; keep in mind that I'm a layman to Python"

>> I am currently unable to complete the sign up for the educational account for GitHub. Will a free (google) account be enough for the workshop or should I pay for additional privileges?

The free GitHub account comes with some free credits. The FAQ section of the Guide on GitHub contains information about how to monitor your usage. Because free account user cannot choose a cheaper model, the credits might be exhausted faster if expensive models are allocated more frequently to your questions. I also mentioned the subscription plan by OpenCode Go, which you might find it more value for money. GitHub allows using third-party models via API. If you click the wheel icon in the lower right corner, you will see buttons for adding other providers.

 

>> I have signed up to Lightning.ai

That's all you need before the Workshop. 

>> I’ve installed the Copilot extension but still can’t get this to load. 

If you click the extension tab on the left vertical bar and use the keyword 'copilot' to search for extensions, you will find the one for GitHub Copilot. Unfortunately, on Lightning.ai, you are required to enable the service. Click that extension and look around to find an Enable button. After clicking it, the chatbox should appear in the right side panel (can be toggled on and off with a button in the upper right corner of Lightning Studio, just like in GitHub Codespace).

Don't hesitate to let me know if you have other questions that you can't figure out yourself or with AI assistance.

Look forward to seeing you on Wednesday.

Best wishes,
Andrew 