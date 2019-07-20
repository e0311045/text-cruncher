import sys
import requests
from bs4 import BeautifulSoup
from gensim.summarization import summarize
import pandas as pd
from flask import Flask, render_template, request, send_file
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
# import tensorflow as tf
# import pickle
# from model import Model
# from utils import build_dict, build_dataset, batch_iter
from datetime import datetime

"""Global Variables"""
non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
final_output = []
final_header = ['Serial No',"Search Query","URL Link","Title of Article","Text Summary"]
current_timestamp = ""

"""Set up Selenium driver"""
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--start-maximized")
# chrome_options.add_argument("-incognito")
chrome_options.add_argument("--disable-popup-blocking")
sel_driver = webdriver.Chrome(executable_path=r"C:\ChromeDriverWin32\chromedriver.exe", chrome_options=chrome_options)

def scrape(lst_query,filename):
    for query in lst_query:
        """Scrape scheduled link from Selenium"""
        url = "https://www.google.com/search?q=" + query
        sel_driver.implicitly_wait(1) #reduce error
        main_url = r"https://www.google.com.sg/"
        sel_driver.get(main_url)
        """Simulates manual log in"""
        username = sel_driver.find_element_by_class_name("gLFyf")
        username.click()
        username.send_keys(query)
        username.submit()
        listOfLinks = [] #resets at the start of each query

        webresults = BeautifulSoup(sel_driver.page_source, "html.parser")
        for info in (webresults.find_all("div", {"class", "g"})):
            links = info.find("a").get('href')
            if "https" not in links:
                continue
            if links in listOfLinks:
                continue
            else:
                listOfLinks.append(links)
        #Serialise Output according to number of links in each query
        final_counter = len(listOfLinks)
        #resets for each query
        counter = 1

        for url in listOfLinks:
            print(url)
            if counter <= final_counter:
                # Pandas- List of Appending
                sub_output = []
                sub_output.append(counter)
                sub_output.append(query)
                sub_output.append(url)
            """attempts to get URL content"""
            try:
                results = get_content(url) #gets content from URL
                if results[1] != "":
                    sub_output.append(results[0]) #Title
                    sub_output.append(results[1]) #Main content
                    final_output.append(sub_output)
                    counter += 1
            except:
                continue

    #Output to Excel File
    df_results = pd.DataFrame(final_output, columns=final_header)
    writer = pd.ExcelWriter('./static/user_pulls/Output_'+filename+'.xlsx', engine='xlsxwriter')
    df_results.to_excel(writer, sheet_name='Results', header=final_header, index=False)

    # modifyng output by style - wrap
    workbook = writer.book
    worksheet = writer.sheets['Results']

    format = workbook.add_format()
    format.set_align('top')
    format.set_text_wrap()
    # Setting the format
    worksheet.set_column('A:A', 10, format)
    worksheet.set_column('B:B', 20, format)
    worksheet.set_column('C:C', 40, format)
    worksheet.set_column('D:D', 20, format)
    worksheet.set_column('E:E', 70, format)

    writer.save()
    writer.close()

    #Clear df
    df_results = None

#Main content Generator with BS4 and Selenium if BS4 fails to scrape
def get_content(url):
    headers = requests.utils.default_headers()
    headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
    })
    r = requests.get(url)
    raw_html = r.content
    soup = BeautifulSoup(raw_html, 'html.parser')
    results = ""
    links = soup.select("body p")
    headers = soup.select("h1")
    header = ""
    if len(headers) != 0:
        header = headers[0].text
    else:
        header =""
    final_text_summary = []
    for link in links:
        try:
            temp = link.text
        except(UnicodeEncodeError):
            temp = link.translate(non_bmp_map)
        except:
            continue

        results = results + temp

    #Check if content can be pulled with BS4
    """word count minimum"""
    validThreshold = 100
    if len(results.split(" ")) < validThreshold:
        #Selenium Pull
        sel_driver.implicitly_wait(1)  # reduce error
        sel_driver.get(url)
        soup = BeautifulSoup(sel_driver.page_source, "html.parser")
        results = ""
        links = soup.select("body p")
        if len(headers) != 0:
            header = headers[0].text
        else:
            header = ""
        print(header)
        for link in links:
            try:
                temp = link.text
            except(UnicodeEncodeError):
                try:
                    temp = link.translate(non_bmp_map)
                except:
                    continue

            results = results + temp

    #otherwise output with BS4 and summariser
    # results = abstractSummarize(summarize(results))
    results = summarize(results)
    print(results)
    final_text_summary.append(header)
    final_text_summary.append(results)
    return final_text_summary

# def abstractSummarize(text):
#     with open("args.pickle", "rb") as f:
#         args = pickle.load(f)
#
#     print("Loading dictionary...")
#     word_dict, reversed_dict, article_max_len, summary_max_len = build_dict("valid", args.toy)
#     print("Loading validation dataset...")
#     valid_x = build_dataset("valid", word_dict, article_max_len, summary_max_len, text, args.toy)
#     valid_x_len = [len([y for y in x if y != 0]) for x in valid_x]
#
#     with tf.Session() as sess:
#         print("Loading saved model...")
#         model = Model(reversed_dict, article_max_len, summary_max_len, args, forward_only=True)
#         saver = tf.train.Saver(tf.global_variables())
#         ckpt = tf.train.get_checkpoint_state("./saved_model/")
#         saver.restore(sess, ckpt.model_checkpoint_path)
#
#         batches = batch_iter(valid_x, [0] * len(valid_x), args.batch_size, 1)
#
#         print("Writing summaries to 'result.txt'...")
#         for batch_x, _ in batches:
#             batch_x_len = [len([y for y in x if y != 0]) for x in batch_x]
#
#             valid_feed_dict = {
#                 model.batch_size: len(batch_x),
#                 model.X: batch_x,
#                 model.X_len: batch_x_len,
#             }
#
#             prediction = sess.run(model.prediction, feed_dict=valid_feed_dict)
#             prediction_output = [[reversed_dict[y] for y in x] for x in prediction[:, 0, :]]
#
#             for line in prediction_output:
#                 summary = ""
#                 for word in line:
#                     if word == "</s>":
#                         break
#                     if word not in summary:
#                         summary = summary + " " + word
#             print(summary)
#             sess.close()
#             return summary


"""---------------FLASK APPLICATION-------------------"""
app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/', methods=['POST'])
def scrape_now():
    #OBtains data from html form and pass it through python to another html page
    queries = request.form['queries'] #receives from html form as String
    lst_queries = queries.split(',') #split by ','
    current_timestamp = datetime.now().strftime('%m%d%Y%H%M%S')
    scrape(lst_queries,current_timestamp)
    return render_template('downloads.html', filename=current_timestamp)

@app.route('/return-file/<filename>')
def return_file(filename):
    return send_file('./static/user_pulls/Output_'+filename+'.xlsx', attachment_filename='Output.xlsx', cache_timeout=0)

@app.route('/about')
def about():
    return render_template('about.html')

#runs the application in debug mode
if __name__ == "__main__":
	app.run(debug=True)