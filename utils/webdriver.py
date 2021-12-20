from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import datetime


def get_value_from_the_web(input_data):
    service = Service(r"C:\Users\gbroll\OneDrive - Deloitte (O365D)\Desktop\Pricing\utils\chromedriver")
    driver = webdriver.Chrome(service=service)
    driver.get("https://goodcalculators.com/black-scholes-calculator/")
    WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.ID, "ez-accept-all"))).click()

    spot_price = driver.find_element(By.ID, "n2")
    strike_price = driver.find_element(By.ID, "n1")
    maturity = driver.find_element(By.ID, "n3")
    volatility = driver.find_element(By.ID, "n4")
    risk_free_rate = driver.find_element(By.ID, "n5")
    dividend_yield = driver.find_element(By.ID, "n6")
    elements = (spot_price, strike_price, maturity, volatility, risk_free_rate, dividend_yield)
    default_value = (input_data["price"], input_data["strike"], (
                datetime.datetime.strptime(input_data["maturity"], "%Y-%m-%d") - datetime.datetime.utcnow()).days / 360,
                         input_data["volatility"] * 100, input_data["risk_free_rate"] * 100,
                         input_data["dividend_yield"] * 100)
    for element, value in zip(elements, default_value):
        element.clear()
        element.send_keys(value)
    driver.find_element(By.ID, "submit").click()

    call_price = float(driver.find_element(By.ID, "info").text.split("$")[1])
    put_price = float(driver.find_element(By.ID, "info1").text.split("$")[1])
    c_delta = float(driver.find_element(By.ID, "Delta_res").text)
    c_gamma = float(driver.find_element(By.ID, "Gamma_res").text)
    c_theta = float(driver.find_element(By.ID, "Theta_res").text)
    c_vega = float(driver.find_element(By.ID, "Vega_res").text)
    c_rho = float(driver.find_element(By.ID, "Rho_res").text)

    driver.execute_script("window.scrollTo(0, 900);")
    element = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='radio'][value='put']")))
    ActionChains(driver).move_to_element(element).click().perform()

    p_delta = float(driver.find_element(By.ID, "Delta_res").text)
    p_gamma = float(driver.find_element(By.ID, "Gamma_res").text)
    p_theta = float(driver.find_element(By.ID, "Theta_res").text)
    p_vega = float(driver.find_element(By.ID, "Vega_res").text)
    p_rho = float(driver.find_element(By.ID, "Rho_res").text)

    driver.close()
    return {"call_price": call_price,
            "put_price": put_price,
            "call_greeks": {
                "delta": c_delta,
                "gamma": c_gamma,
                "theta": c_theta,
                "rho": c_rho,
                "vega": c_vega},
            "put_greeks": {
                "delta": p_delta,
                "gamma": p_gamma,
                "theta": p_theta,
                "rho": p_rho,
                "vega": p_vega}
            }
