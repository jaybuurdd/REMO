import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('OPEN_AI_API_KEY')
client = OpenAI(api_key=api_key)


def chatgpt_review(image_urls) -> str:
    # print(f"\n{url}\n")
    input = '''

        Refer to the user in second person.
        

        Their contact info should be at the top.


        Proof read their summaries if they provide one and suggest a revised version for them to see.


        Their social media's should be shared if possible (e.g LinkedIn, GitHub) if its missing.


        Remind user to double check all links are clickable and blue and/or underlined.


        Job experience should be 3-4 strong bullet points. They shouldn't use metric numbers like "`80%` increase on user engagement", without mentioning how they got the caluclations.


        The job bullet points should have 1-2 that mention a feature or system design they implemented at a specified job.


        If their job expereince bullet points are to vague give examples of how they could improve by giving scenario examples that they should only use for reference.

        
        Education should show school first then degree, in this format:

            The University of Chicago
            B.S in Computer Science


        If they have full-time job experience Education should go at the bottom (any job expereince other than internship or research).\
        
        
        If they have a Publication type section they should provide links to their paper's if possible.


        Projects should go under job experience and should be a brief description of the project. If they have a lot of job expereince or 3 strong bullet points talking about tech they utilized if they don't have much expereince.

        
        Projects should have clickable links to Github and/or live site if possible.


        Users shouldn't have personality or interests sections in their resume or anything irrelevant like gender, favorite foods, etc.


        A resume can have a interest section if they have no experience.


        Make a note to the user that you can't tell how long their resume is but unless they have 10+ years expereince their resume really should only be 2-3 pages long.


        Give your best assessment of the formatting of their resume and if its readable.


        Note that the resume can put keywords in bold like tech used mentioned in their sentences.


        Only Project section and Job section should have bullet points.


        If the user provide a list of technologies used underneath each job They can have that as long as there's no bullet points and they highlight the list in bold.


        Skills shouldn't have a long list of bullet points. They can put them in their own categories or just list them like this:

            Git, Java, Python, Redis, SQL, NoSQL

        Only mention these things if they go against the guidlines above.

        '''
    try:
         # Prepare the user message content with text and images
        user_content = [
            {
                "type": "text",
                "text": f"Critique this resume following these guidelines:\n\n{input}\n\nAnything else you might notice that doesn't break the guidelines you can mention as well."
            }
        ]

        # Append image URLs
        user_content.extend(
            {"type": "image_url", "image_url": {"url": url}} for url in image_urls
        )

        # Create the messages list for the API call
        messages = [
            {
                "role": "system",
                "content": "You review resumes and only provide improvements that need to be made to them."
            },
            {
                "role": "user",
                "content": user_content
            }
        ]
        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=messages,
            max_tokens=4096
        )

        message = response.choices[0].message
        content = message.content
            
        # print(f"\n\n {content}")
        # print(f"finish: {response.choices[0].finish_reason}")
        return content
    except Exception as e:
        print(f"Error processing review: {e}")
        raise(e)

    # def chatgpt_review(text) -> str:
    #     print(f"\n{text}\n")
    #     response = client.chat.completions.create(
    #         model="gpt-3.5-turbo",
    #         messages=[
    #             {"role": "system", 
    #             "content": "You review resume's and only provide improvements that need to be made to them."},
    #             {
    #                 "role": "user",
    #                 "content": [
    #                     {"type": "text", "text": f"Critique this resume this resume:\n\n{text}"},
    #                 ],
    #             }
    #         ],
    #     )

    #     message = response.choices[0].message
    #     content = message.content
        
    #     print(f"\n\n {content}")
    #     return content