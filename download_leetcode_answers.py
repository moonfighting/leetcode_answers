import urllib
import urllib2
import cookielib
import os
import sys
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

leetcode_url = "https://leetcode.com"
login = "/accounts/login/"
userID = "huyi100"
password = "huyi6723312"
token = ""

language_dict = {'python':'py', 'cpp':'cpp', 'java':'java', 
                 'csharp':'cs','javascript':'js', 'ruby':'rb',
                 'python':'py'
                }


def get_login_html(userID, password, token, cookie, opener):
    data ={"login": userID, "password" : password, "csrfmiddlewaretoken" : token }
    postdata = urllib.urlencode(data)
    login_url = leetcode_url + login

    headers = {'Referer': "https://leetcode.com/accounts/login/",
           'Content-Type': 'application/x-www-form-urlencoded',
           'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:29.0) Gecko/20100101 Firefox/29.0',
           'Host': 'leetcode.com'}
    cookies = {
        '_gat': '1',
        'csrftoken': token,
        '_ga': 'GA1.2.239090711.1445325270'
    }

    #opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
    req = urllib2.Request(url = login_url, data = postdata, headers = headers)
    result = opener.open(req)
    print result.code
    response_html = result.read()
    return response_html
  

def get_problem_lists(response_html):
    
    problem_urls = []
    problem_names = []
    soup = BeautifulSoup(response_html)
    tbody_tag = soup.find_all('tbody')[1]
    tr_tags = tbody_tag.find_all('tr')
    for tr_tag in tr_tags:
        td_tag = tr_tag.find_all('td')[2]
        if td_tag.i == None:
                problem_url = leetcode_url + str(td_tag.a['href'])
                problem_title = str(td_tag.a.string)
                problem_urls.append(problem_url)
                problem_names.append(problem_title)
    
    return problem_urls, problem_names

def main_func():
   
    login_url = leetcode_url + login

    driver = webdriver.Firefox()
    driver.implicitly_wait(10)
    driver.get(login_url)

    element = driver.find_element_by_id("id_login")
    element.send_keys(userID)
    element = driver.find_element_by_id("id_password")
    element.send_keys(password)

    submin_button = driver.find_element_by_xpath('//div[@class="form-group"]/button')
    submin_button.click()                             #login                               
    htm = driver.page_source.encode('utf-8')
    problem_urls, problem_names = get_problem_lists(htm) # get problem list
    problem_urls = problem_urls[0: 100: 10]
    for problem_url in problem_urls:
        problem_name = problem_url.split('/')[-2]
        problem_url = problem_url + 'submissions/'
        print problem_name

        driver.get(problem_url)
        try:
            tbody = driver.find_element_by_tag_name('tbody')
        except Exception, e:
            print problem_name, ':unsolved'
            continue
        trs = tbody.find_elements_by_tag_name('tr')
        accepted_urls = []
        for tr in trs:                                  #find accepted answers
            tds = tr.find_elements_by_tag_name('td')
            status_td = tds[2]
            run_time_td = tds[3]
            try:
                a_tag = status_td.find_element_by_tag_name('a')
                status = a_tag.find_element_by_tag_name('strong').text
                if status == 'Accepted':
                    result_url = status_td.find_element_by_tag_name('a').get_attribute('href')
                    accepted_urls.append(result_url)
            except Exception, e:
                print problem_name 
                pass
        
        if not accepted_urls:
            print problem_name, ':no accepted answers'
            exit
        for accepted_url in accepted_urls:
            driver.get(accepted_url)
            get_accepted_code(driver, problem_name)

    driver.quit()



def get_accepted_code(driver, problem_name):
    answer_html =  driver.page_source.encode('utf-8')
    answer_soup = BeautifulSoup(answer_html, from_encoding = 'utf-8')
    line_groups = driver.find_elements_by_class_name('ace_line_group')
    run_time = driver.find_element_by_id('result_runtime').text
    code_languate = driver.find_element_by_id('result_language').text
    code_file_suffix = language_dict[code_languate]
    code_file_name = problem_name + '_' + run_time.replace(' ', '_') + '.' + code_file_suffix
    tab_num = 0
    right_tab = False
    code_file = open(code_file_name, 'w')
    for line_group in line_groups:
        ace_line = line_group.find_element_by_class_name('ace_line')
        spans = ace_line.find_elements_by_tag_name('span')
        line_code = ''
        for span in spans:
            if right_tab:
                tab_num += 1
                right_tab = False
            if span.text == '{':
                right_tab = True
            if span.text == '}':
                tab_num -= 1


            line_code = line_code + span.text + ' '
            
        code_file.write(tab_num * '\t' + line_code + '\n') 

    code_file.close()
    #os.system('indent -linux -nve %s' % code_file_name)
    #os.system('rm %s~' %code_file_name)




if __name__ == '__main__':

    login_url =leetcode_url + login
    cj = cookielib.CookieJar() 
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj)) 
    urllib2.install_opener(opener)
    res = opener.open(login_url) 
    token = ""
    for index, item in enumerate(cj):
        token = item.value
    print token
    #htm = get_login_html(userID, password, token, cj, opener)
    #problem_urls, problem_names = get_problem_lists(htm)
    main_func()
