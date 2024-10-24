import requests
from bs4 import BeautifulSoup
import os, json
import shutil

baseURL = 'https://www.indiabix.com'
des_count = 0#just tracking

def handle_image(u):
    url = baseURL+u
    filename = '../data_img/'+'_'.join(u.split('/')[-2:])
    if os.path.exists(filename):
        return filename
    response = requests.get(url, stream=True)
    print('Image', filename)
    with open(filename, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response
    return filename

def get_content(e):
    rc=[]
    for i in e.contents:
        s = i.string
        if not s:
            s=i.get_text()
        if i.name==None:
            rc.append(['span', s])
        elif i.name=='p' or i.name=='i' or i.name=='sup' or i.name=='span' or i.name=='sub' or i.name=='b':
            rc.append([i.name, s])
        elif i.name=='img':
            rc.append(['img', handle_image(i['src'])])
        elif i.name=='br':
            rc.append(['br'])
        else:
            print(i)
            raise i.name
    return rc

#u is url or soap el
def crawl_content(u):
    a_list = []
    soup=u
    if isinstance(u, str):
        print(u)
        url = baseURL+u
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
    q_div = soup.find_all("div", {"class": 'bix-div-container'})
    for i in q_div:
        q_text = i.find("td", {"class": 'bix-td-qtxt'})
        options = map(get_content, i.find_all("td", {"class": 'bix-td-option'})[1::2])
        q_des = i.find("div", {"class": 'bix-ans-description'})
        q_ans = i.find("div", {"class": 'bix-div-answer'}).contents[1].get_text()[-1]
        ro = {'que': get_content(q_text), 'options': list(options), 'ans': q_ans}
        if q_des.get_text().strip() != 'No answer description available for this question. Let us discuss.':
            ro['des'] = get_content(q_des)
            global des_count
            des_count+=1
        a_list.append(ro)
    return a_list

def crawl_section(u):
    soup=u
    if isinstance(u, str):
        url = baseURL+u
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
    a_list = crawl_content(soup)
    pager_p = soup.find("p", {"class": 'mx-pager'})
    if not pager_p:
        return a_list
    links = pager_p.find_all('a')[:-1]
    for i in links:
        a_list.extend(crawl_content(i['href']))
    return a_list

def crawl_categories(name, u):
    url = baseURL+u
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    sections_div = soup.find("div", {"class": 'div-top-left'})
    sections = sections_div.find_all('li')
    print('Section 1')
    a_list = [crawl_section(soup)]
    for i in sections[1:]:
        text= i.get_text()
        c = text.rfind(' ')
        print(f'Section {text[c:]}')
        a_list.append(crawl_section(i.contents[0]['href']))
    return a_list

def crawl_main():
    url = baseURL+'/civil-engineering/questions-and-answers/'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    categories_div = soup.find_all("div", {"class": 'div-topics-index'})
    for k in categories_div: 
        categories = k.find_all('a')
        for i in categories:
            title = i.get_text()
            filename = f"../data/{title}.json"
            print(title, des_count)
            # des_count, only one description in survey
            if not os.path.exists(filename):
                p = crawl_categories(i.get_text(),i['href'])
                with open(filename, 'w') as f:
                    json.dump(p, f)

def main():
    crawl_content('/civil-engineering/applied-mechanics/044004');

if __name__ == "__main__":
    crawl_main()
    #main()
