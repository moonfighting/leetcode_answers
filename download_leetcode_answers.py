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
#userID = ""
#password = ""
#save_dir = ""
language_dict = {'python':'py', 'cpp':'cpp', 'java':'java', 
                 'csharp':'cs','javascript':'js', 'ruby':'rb',
                 'python':'py'}

def get_problem_lists(response_html):
    
    problem_urls = []
    soup = BeautifulSoup(response_html)
    tbody_tag = soup.find_all('tbody')[1]
    tr_tags = tbody_tag.find_all('tr')
    for tr_tag in tr_tags:
        td_tag = tr_tag.find_all('td')[2]
        if td_tag.i == None:
                problem_url = leetcode_url + str(td_tag.a['href'])
                problem_title = str(td_tag.a.string)
                problem_urls.append(problem_url)
                
    
    return problem_urls

def main_func(userID, password, save_dir):
   
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
    problem_urls = get_problem_lists(htm) # get problem list
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
    os.path.join(save_dir, code_file_name)
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

    if len(sys.argv) < 3:
        print "Usage: python download_leetcode_answers [user ID] [password] [save_dir]"
        exit()


    user_ID = sys.argv[1]
    password = sys.argv[2]
    save_dir = sys.argv[3]
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)

    main_func(user_ID, password, save_dir)
