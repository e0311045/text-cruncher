import sys
# import codecs
import requests
from bs4 import BeautifulSoup
from gensim.summarization import summarize
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime
from flask import Flask, render_template, request, send_file
from flask_mail import Mail, Message

""" --------------------Scrape content-------------------------- """
"""Global Variables"""
non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
final_output = []
# final_header = ['Serial No',"Search Query","URL Link","Title of Article","Text Summary","Abstract"]
final_header = ['Serial No',"Search Query","URL Link","Title of Article","Text Summary"]
abstract_Txt = ""

"""Set up Selenium driver"""
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--start-maximized")
# chrome_options.add_argument("-incognito")
chrome_options.add_argument("--disable-popup-blocking")
chrome_options.binary_location = GOOGLE_CHROME_BIN
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
sel_driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH,chrome_options=chrome_options)

def scrape(lst_query,withAbstract,filename):

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
                results = get_content(url,withAbstract,filename) #gets content from URL
                if results[1] != "":
                    sub_output.append(results[0]) #Title
                    sub_output.append(results[1]) #Main content
                    # if(counter==final_counter):
                    #     abstract_Txt = abstractSummarize('Process.txt')
                    # sub_output.append(abstract_Txt)
                    final_output.append(sub_output)
                    counter += 1
            except:
                continue

    # Output to Excel File
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
    worksheet.set_column('E:E', 70, format)
    # Clear df
    df_results = None
    writer.save()
    writer.close()

#Main content Generator with BS4 and Selenium if BS4 fails to scrape
def get_content(url,withAbstract,filename):
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

    # if(withAbstract):
    #     #Save a text file with original text for abstract summary
    #     with codecs.open("Process.txt","a",encoding='utf8') as f:
    #         try:
    #             f.write(results)
    #         except(UnicodeEncodeError):
    #             f.write(results.translate(non_bmp_map))

    #otherwise output with BS4 and summariser
    results = summarize(results)
    print(results)
    final_text_summary.append(header)
    final_text_summary.append(results)
    return final_text_summary


# def abstractSummarize(filepath):
#     with open("args.pickle", "rb") as f:
#         args = pickle.load(f)
#
#     print("Loading dictionary...")
#     word_dict, reversed_dict, article_max_len, summary_max_len = build_dict("valid", args.toy)
#     print("Loading validation dataset...")
#     valid_x = build_dataset("valid", word_dict, article_max_len, summary_max_len, filepath, args.toy)
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
#         print("Writing summaries")
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
#             # return line
#             abstract = ""
#             # Writing to text file
#             #with open("result.txt", "a") as f:
#
#             for line in prediction_output:
#                 summary = list()
#                 for word in line:
#                     if word == "</s>":
#                         break
#                     if word == "black" or word == "bosch" or word == "<" or word == "unk" or word == ">":
#                         continue
#                     if word not in summary:
#                         summary.append(word)
#                         abstract = abstract + " " + word
#         os.remove('./static/abst_file/Process'+filename+'.txt')
#         return abstract

"""-------------------------------FLASK APPLICATION------------------------------------"""
app = Flask(__name__)

"""Flask Mail Configuration"""
app.config['TESTING'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_DEBUG'] = True #same as Debug mode
app.config['MAIL_USERNAME'] = 'textcruncher@gmail.com'
app.config['MAIL_PASSWORD'] = 'r3s0lute'
app.config['MAIL_DEFAULT_SENDER'] = None
app.config['MAIL_MAX_EMAILS'] = None
app.config['MAIL_SUPPRESS_SEND'] = False #same as TESTING
app.config['MAIL_ASCII_ATTACHMENTS'] = False #keyboard characters
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

"""Flask Mail Sending"""
mail= Mail(app)

@app.route('/send-mail/', methods=['POST'])
def send_mail():
    receiver = []
    emailadd = request.form['email_address']
    receiver = emailadd.split(',')
    # receiver.append()  # receives from html form as String
    text = request.form['msg_txt']  # receives from html form as String
    filename = request.form['fileName']
    with app.open_resource('./static/user_pulls/Output_'+filename+'.xlsx') as fp:
        msg = Message('Below is an Attached File of your Query Results', sender='textcruncher@gmail.com', recipients=receiver)
        msg.attach('Output_'+filename+'.xlsx', 'file/xlsx', fp.read())
        msg.body = text
        mail.send(msg)
    return render_template('downloads.html', filename=filename)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def scrape_now():
    #OBtains data from html form and pass it through python to another html page
    queries = request.form['queries'] #receives from html form as String
    # withAbstract = request.form['inc_exc']
    lst_queries = queries.split(',') #split by ','
    current_timestamp = datetime.now().strftime('%m%d%Y%H%M%S')
    # if(withAbstract=='True'):
    #     withAbstract = True
    # else:
    #     withAbstract = False
    # scrape(lst_queries,withAbstract,current_timestamp)
    scrape(lst_queries, current_timestamp)
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
