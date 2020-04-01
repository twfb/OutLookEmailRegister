import os
import requests
import time
import re
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver import Firefox, FirefoxOptions, DesiredCapabilities
from selenium.webdriver.common.proxy import ProxyType, Proxy
from datetime import datetime


headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'deflate',
    'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
    'cache-control': 'max-age=0',
    'dnt': '1',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
}
url = 'https://signup.live.com/signup'
check_timeout = 1


def find_element_by_css_selector(driver, css_selector):
    try:
        return driver.find_element_by_css_selector(css_selector)
    except (NoSuchElementException, ElementNotInteractableException):
        time.sleep(check_timeout)
        return find_element_by_css_selector(driver, css_selector)


def find_elements_by_css_selector(driver, css_selector):
    try:
        return driver.find_elements_by_css_selector(css_selector)
    except (NoSuchElementException, ElementNotInteractableException):
        time.sleep(check_timeout)
        return find_elements_by_css_selector(driver, css_selector)


def find_element_by_link_text(driver, link_text):
    try:
        return driver.find_element_by_link_text(link_text)
    except (NoSuchElementException, ElementNotInteractableException):
        time.sleep(check_timeout)
        return find_element_by_link_text(driver, link_text)


def find_elements_by_tag_name(driver, tag_name, target_number=None):
    try:
        l = driver.find_elements_by_tag_name(tag_name)
        if not target_number:
            return l
        if len(l) == target_number:
            return l
        else:
            return find_elements_by_tag_name(driver, tag_name, target_number)
    except (NoSuchElementException, ElementNotInteractableException):
        time.sleep(check_timeout)
        return find_elements_by_tag_name(driver, tag_name, target_number)


def find_element_by_tag_name(driver, tag_name):
    try:
        return driver.find_element_by_tag_name(tag_name)
    except (NoSuchElementException, ElementNotInteractableException):
        time.sleep(check_timeout)
        return find_element_by_tag_name(driver, tag_name)


def set_global_chek_timeout(ip_list,  max_bad_number=None):
    global check_timeout
    if not ip_list:
        print(ip_list)
        raise Exception('ip_list is None')
    bad_number = 0
    success_number = 0
    if max_bad_number is None:
        max_bad_number = len(ip_list)/2
    for ip, port, tp in ip_list:
        tp = tp.lower()
        try:
            ip_url = '{}:{}'.format(ip, port)
            requests.get(url=url, headers=headers, proxies={
                         tp: '{}://'.format(tp)+ip_url}, timeout=check_timeout)
            success_number += 1
        except Exception:
            bad_number += 1
        print('try set timeout={} \t success:{} \t fail:{}'.format(
            check_timeout, success_number, bad_number))

        if success_number >= len(ip_list) - max_bad_number:
            with open('check_timeout.txt', 'w') as f:
                f.write(str(check_timeout))
            return check_timeout

        if bad_number >= max_bad_number:
            check_timeout += 1
            if check_timeout >= 10:
                raise
            return set_global_chek_timeout(ip_list, max_bad_number)


def get_ip_list():
    global check_timeout
    d = datetime.now()
    year = d.year
    month = d.month
    day = d.day
    hour = d.hour
    req_url = 'https://ip.ihuan.me/today/{}/{:02d}/{{:02d}}/{{:02d}}.html'.format(
        year,
        month
    )
    e = False
    while not e:
        try:
            response = requests.get(req_url.format(
                day, hour), headers=headers)
            e = True
            print('get ip list page success')
        except Exception as ex:
            print(ex)
            time.sleep(2)
            e = False
            hour -= 1
            if hour == 0:
                raise Exception('get ip timeout')
    ip_list = re.findall(
        r'<br>([\d\.]*?):(\d*)@(.*?)#',
        response.text,
        re.S
    )
    l = []
    with open('check_timeout.txt', 'r') as f:
        f_read = f.read()
        if f_read:
            l = list(map(int, f_read.split(' ')))
    if l and [year, month, day, hour] == l[:-1]:
        check_timeout = l[-1]
    else:
        set_global_chek_timeout(ip_list[:5])
    for ip, port, tp in ip_list:
        tp = tp.lower()
        port = int(port)
        try:
            ip_url = '{}:{}'.format(ip, port)
            with open('used_ip.txt', 'r') as f:
                if ip in f.read():
                    continue
            with open('used_ip.txt', 'a+') as f:
                f.write(ip + '\n')
            print('test ip: {} \t time_out: {}'.format(ip_url, check_timeout))
            if requests.get(url=url, headers=headers, proxies={tp: '{}://'.format(tp)+ip_url}, timeout=check_timeout).status_code == 200:
                print('suceess: ' + ip_url)
                yield ip_url
        except Exception as ex:
            print(ex)


def run_driver(driver, email, password):
    driver.get(url)
    time.sleep(check_timeout)
    find_element_by_css_selector(driver, '#liveSwitch').click()
    find_element_by_css_selector(driver, '#MemberName').send_keys(email)
    find_element_by_css_selector(driver, '#iSignupAction').click()
    if 'alert alert-error col-md-24' in driver.page_source:
        return 'exist'
    find_element_by_css_selector(
        driver, '#PasswordInput').send_keys(password)
    find_element_by_css_selector(driver, '#iOptinEmail').click()
    find_element_by_css_selector(driver, '#iSignupAction').click()
    find_element_by_css_selector(driver, '#LastName').send_keys('1')
    find_element_by_css_selector(driver, '#FirstName').send_keys('1')
    find_element_by_css_selector(driver, '#iSignupAction').click()
    find_element_by_css_selector(
        driver, '#BirthYear option:nth-child(3)').click()
    find_element_by_css_selector(
        driver, '#BirthMonth option:nth-child(10)').click()
    find_element_by_css_selector(
        driver, '#BirthDay option:nth-child(6)').click()
    find_element_by_css_selector(driver, '#iSignupAction').click()

    try:

        while True:
            key = ''
            e = find_elements_by_tag_name(driver, 'input', 5)[0]
            t_url = driver.current_url
            while not key or 'text-align: left; display: inline;' in driver.page_source:
                key = input('Input:')
            e.send_keys(key)
            find_element_by_css_selector(driver, '#iSignupAction').click()
            if t_url != driver.current_url:
                return True
    except Exception:
        return False


i = 0
with open('i.txt', 'r') as f:
    i = int(f.read())
for ip_url in get_ip_list():
    i += 1
    options = FirefoxOptions()
    proxy = Proxy({
        'proxyType': ProxyType.MANUAL,
        'httpProxy': ip_url
    })
    desired_capabilities = DesiredCapabilities().FIREFOX
    desired_capabilities['pageLoadStrategy'] = 'none'
    driver = Firefox(
        options=options, desired_capabilities=desired_capabilities, proxy=proxy)
    email, password = 'ssAd{}ssAd'.format(i), 'sKill#{}#sKill'.format(i)
    result = run_driver(driver, email, password)
    while result == 'exist':
        with open('pass.txt', 'a+') as f:
            f.write(email + ' ' + password + '\n')
        with open('i.txt', 'w') as f:
            f.write(str(i))
        print('Already Register Account {}:{}'.format(email, password))
        result = run_driver(driver, email, password)
        i += 1

    if result:
        sleep_time = 0
        while 'account.microsoft.com' not in driver.current_url:
            sleep_time += 1
            time.sleep(check_timeout)
            if sleep_time >= 10:
                break
        if sleep_time >= 10:
            print('waiting time too long')
            i -= 1
        else:
            with open('pass.txt', 'a+') as f:
                f.write(email + ' ' + password + '\n')
            with open('i.txt', 'w') as f:
                f.write(str(i))
            print('Success Register Account {}:{}'.format(email, password))
    else:
        print('Fail')
        i -= 1
    driver.close()
    driver.quit()
