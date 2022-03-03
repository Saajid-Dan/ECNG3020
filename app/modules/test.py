def runrun():
    from selenium import webdriver
    from selenium.webdriver.firefox.options import Options
    from PIL import Image

    options = Options()
    options.headless = True

    #set chromodriver.exe path
    driver = webdriver.Firefox(options=options)
    driver.maximize_window()
    #launch URL
    driver.get('http://127.0.0.1:5000')
    #get window size
    s = driver.get_window_size()
    #obtain browser height and width
    w = driver.execute_script('return document.body.parentNode.scrollWidth')
    h = driver.execute_script('return document.body.parentNode.scrollHeight')
    #set to new window size
    driver.set_window_size(w, h)
    #obtain screenshot of page within body tag
    driver.find_element_by_tag_name('body').screenshot("tutorialspoint.png")
    driver.set_window_size(s['width'], s['height'])
    driver.quit()

    im = Image.open("./tutorialspoint.png")
    im = im.convert('RGB')
    im.save("./tutorialspoint.pdf")
# runrun()