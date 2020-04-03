import os
import requests
import time
import re
import json
import schedule
import tempfile

from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver import DesiredCapabilities, Chrome, ChromeOptions
from datetime import datetime
from random import randrange, choice
from selenium.webdriver.common import utils


# verification code Identification settings
code_url = 'http://apigateway.jianjiaoshuju.com/api/v_1/yzmCustomized.html'
code_headers = {
    'appCode': 'X',
    'appKey': 'X',
    'appSecret': 'X'
}



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
check_timeout = 0
sign_list = ['~', '!', '@', '#', '$', '%', '^', '&', '*',
             '(', ')', '_+', '<', '>', '?', ':', '"', '{', '}', '|']
name_list = [
    'Emma',
    'Olivia',
    'Ava',
    'Isabella',
    'Sophia',
    'Charlotte',
    'Mia',
    'Amelia',
    'Harper',
    'Evelyn',
    'Abigail',
    'Emily',
    'Elizabeth',
    'Mila',
    'Ella',
    'Avery',
    'Sofia',
    'Camila',
    'Aria',
    'Scarlett',
    'Victoria',
    'Madison',
    'Luna',
    'Grace',
    'Chloe',
    'Penelope',
    'Layla',
    'Riley',
    'Zoey',
    'Nora',
    'Lily',
    'Eleanor',
    'Hannah',
    'Lillian',
    'Addison',
    'Aubrey',
    'Ellie',
    'Stella',
    'Natalie',
    'Zoe',
    'Leah',
    'Hazel',
    'Violet',
    'Aurora',
    'Savannah',
    'Audrey',
    'Brooklyn',
    'Bella',
    'Claire',
    'Skylar'
]

last_image_data = ''
last_code = ''


def find_element_by_css_selector(driver, css_selector):
    try:
        time.sleep(0.1)
        return driver.find_element_by_css_selector(css_selector)
    except Exception:
        time.sleep(check_timeout)
        return find_element_by_css_selector(driver, css_selector)


def find_elements_by_css_selector(driver, css_selector):
    try:
        time.sleep(0.1)
        return driver.find_elements_by_css_selector(css_selector)
    except Exception:
        time.sleep(check_timeout)
        return find_elements_by_css_selector(driver, css_selector)


def find_element_by_link_text(driver, link_text):
    try:
        time.sleep(0.1)
        return driver.find_element_by_link_text(link_text)
    except Exception:
        time.sleep(check_timeout)
        return find_element_by_link_text(driver, link_text)


def find_elements_by_tag_name(driver, tag_name, target_number=None, try_times=None):
    time.sleep(0.1)
    if try_times <= 0:
        raise Exception('Can not find element.')
    if try_times is not None:
        try_times -= 1
    try:
        l = driver.find_elements_by_tag_name(tag_name)
        if target_number is None:
            return l
        if len(l) == target_number:
            return l
        else:
            time.sleep(check_timeout)
            return find_elements_by_tag_name(driver, tag_name, target_number, try_times)
    except Exception:
        time.sleep(check_timeout)
        return find_elements_by_tag_name(driver, tag_name, target_number, try_times)


def find_element_by_tag_name(driver, tag_name):
    try:
        time.sleep(0.1)
        return driver.find_element_by_tag_name(tag_name)
    except Exception:
        time.sleep(check_timeout)
        return find_element_by_tag_name(driver, tag_name)


def get_code(img_data):
    global last_image_data
    global last_code
    if last_image_data == img_data:
        return last_code
    last_image_data = img_data
    data = {
        'v_pic': img_data,
        'pri_id': 'ne',
    }

    response = requests.post(code_url, headers=code_headers, data=data)
    code = json.loads(response.text)['v_code']
    last_code = code
    print('code is {}'.format(code))
    return code


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
        print('try to set timeout={} \t success:{} \t fail:{}'.format(
            check_timeout, success_number, bad_number))

        if bad_number > max_bad_number:
            check_timeout += 1.5
            if check_timeout >= 10:
                raise TimeoutError
            return set_global_chek_timeout(ip_list, max_bad_number)

        if success_number > len(ip_list) - max_bad_number:
            d = datetime.now()
            with open('check_timeout.txt', 'w') as f:
                f.write('{} {} {} {} {}'.format(
                    d.year, d.month, d.day, d.hour, check_timeout))
            return check_timeout


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
    ip_list = []
    while True:
        try:
            cur_url = req_url.format(day, hour)
            print('try to get ip list page: ' + cur_url)
            response = requests.get(cur_url, headers=headers)
            ip_list = re.findall(
                r'<br>([\d\.]*?):(\d*)@(.*?)#',
                response.text,
                re.S
            )
            if ip_list:
                break
            hour -= 1
        except Exception as ex:
            print(ex)
            time.sleep(2)
            hour -= 1
            if hour == 0:
                raise Exception('get ip timeout')
    print('get ip list page success')
    if os.path.exists('check_timeout.txt'):
        l = []
        with open('check_timeout.txt', 'r') as f:
            f_read = f.read()
            if f_read:
                l = list(map(float, f_read.split(' ')))
        if l and [year, month, day, hour] == l[:-1]:
            check_timeout = l[-1]
        else:
            set_global_chek_timeout(ip_list[-5:])
    else:
        set_global_chek_timeout(ip_list[-5:])
    used_ip = ''
    if os.path.exists('used_ip.txt'):
        with open('used_ip.txt', 'r') as f:
            used_ip = f.read()
    return [[tp, '{}:{}'.format(ip, port)] for ip, port, tp in ip_list if ip not in used_ip]


def register_email(driver, email, password):
    driver.get(url)
    time.sleep(check_timeout*2)
    sleep_timess = 0
    while True:
        try:
            driver.find_element_by_css_selector('#liveSwitch').click()
            break
        except Exception:
            time.sleep(check_timeout)
            sleep_timess += 1
            if sleep_timess > 10:
                return False
    while True:
        try:
            find_element_by_css_selector(driver, '#MemberName').clear()
            find_element_by_css_selector(
                driver, '#MemberName').send_keys(email)
            find_element_by_css_selector(driver, '#iSignupAction').click()
            break
        except Exception as e:
            time.sleep(check_timeout)
    sleep_timess = 0
    while driver.title != 'Create a password' and driver.title != '创建密码':
        time.sleep(check_timeout)
        sleep_timess += 1
        if sleep_timess > 15:
            return 'exist'
    find_element_by_css_selector(
        driver, '#PasswordInput').send_keys(password)
    find_element_by_css_selector(driver, '#iOptinEmail').click()
    find_element_by_css_selector(driver, '#iSignupAction').click()
    time.sleep(check_timeout)
    find_element_by_css_selector(
        driver, '#LastName').send_keys(choice(name_list))
    find_element_by_css_selector(
        driver, '#FirstName').send_keys(choice(name_list))
    find_element_by_css_selector(driver, '#iSignupAction').click()
    time.sleep(check_timeout)
    find_element_by_css_selector(
        driver, '#BirthYear option:nth-child({})'.format(randrange(2, 25))).click()
    find_element_by_css_selector(
        driver, '#BirthMonth option:nth-child({})'.format(randrange(2, 11))).click()
    find_element_by_css_selector(
        driver, '#BirthDay option:nth-child({})'.format(randrange(2, 22))).click()
    find_element_by_css_selector(driver, '#iSignupAction').click()
    time.sleep(check_timeout)
    t_url = driver.current_url
    try:
        while True:
            code_element = find_elements_by_tag_name(driver, 'input', 5, 2)[0]
            code_element.clear()
            code_element.send_keys(
                get_code(
                    find_elements_by_tag_name(
                        driver, 'img', 5, 2
                    )[-1].screenshot_as_base64
                )
            )
            find_element_by_css_selector(driver, '#iSignupAction').click()
            time.sleep(check_timeout)
            try_times = 0
            while t_url == driver.current_url:
                time.sleep(check_timeout)
                try:
                    driver.find_element_by_css_selector(
                        '#iSignupAction').click()
                except Exception:
                    pass
                try_times += 1
                if try_times > 8:
                    break
                if t_url != driver.current_url:
                    return True
    except Exception as e:
        print(e)
        return False


def get_email_password():
    def _get_random_sign():
        return choice(sign_list)

    def _get_random_char(is_low=None):
        if is_low is None:
            r = randrange(0, 2)
        elif is_low is True:
            r = 0
        else:
            r = 1

        if r == 0:
            return chr(randrange(65, 91))
        else:
            return chr(randrange(97, 123))

    email = str(randrange(0, 10)).join(_get_random_char() for i in range(5))
    password = (
        str(randrange(0, 100)) + _get_random_sign()
    ).join(
        _get_random_char(True) + _get_random_char() + _get_random_char(False) for i in range(3)
    )
    return email, password


def start_register(driver):
    email, password = get_email_password()
    result = register_email(driver, email, password)
    while result == 'exist':
        print('Already Register Account {}@outlook.com'.format(email))
        email, password = get_email_password()
        result = register_email(driver, email, password)

    if result:
        sleep_times = 0
        while 'account.microsoft.com' not in driver.current_url:
            sleep_times += 1
            time.sleep(check_timeout)
            if sleep_times >= 20:
                break
        if sleep_times >= 10:
            print('waiting time too long')
        else:
            with open('pass.txt', 'a+') as f:
                f.write(email + '@outlook.com ' + password + '\n')
            print('Success Register Account {}@outlook.com'.format(email))
            return True
    else:
        print('Fail')
        return False


def create_driver(tp, ip_port):
    port = utils.free_port()
    options = ChromeOptions()
    desired_capabilities = DesiredCapabilities().CHROME
    desired_capabilities['pageLoadStrategy'] = 'none'
    os.popen(
        'chrome.exe --remote-debugging-port={} --user-data-dir={} --proxy-server={}={}'.format(
            port, tempfile.mkdtemp(), tp, ip_port)
    )
    options.add_experimental_option(
        'debuggerAddress', '127.0.0.1:{}'.format(port))
    driver = Chrome(
        options=options, desired_capabilities=desired_capabilities)
    driver.set_window_position(0, 0)
    driver.set_window_size(700, 600)
    return driver


def run_driver():
    consecutive_fail_number = 0
    try:
        for tp, ip_port in get_ip_list():
            if datetime.now().minute == 10 or consecutive_fail_number > 10:
                break
            print('Proxy: {}://{}'.format(tp, ip_port))
            driver = create_driver(tp, ip_port)
            register_success = start_register(driver)
            driver.close()
            if register_success:
                consecutive_fail_number = 0
            if not register_success:
                consecutive_fail_number += 1
    except Exception as e:
        print(e)
    return schedule.every().minute.at(':10').do(run_driver)


if __name__ == '__main__':
    run_driver()
