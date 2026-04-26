*** Settings ***
Library    Browser
Suite Setup    New Browser    headless=True
Suite Teardown    Close Browser

*** Variables ***
${URL}           http://127.0.0.1:8000
${PRODUCT_URL}   ${URL}/products/xnano-mini-portable-projector/
${CHECKOUT_URL}  ${URL}/orders/checkout/

*** Test Cases ***
Rapid Multiple Orders Test
    [Documentation]    Places two orders rapidly to verify background threads handle product strings correctly.
    Place Guest Order    John    Doe    john@example.com    1234567890    Street 1    City 1    State 1    123456    India    UTR123456789
    Place Guest Order    Jane    Smith    jane@example.com    9876543210    Street 2    City 2    State 2    654321    India    UTR987654321

*** Keywords ***
Place Guest Order
    [Arguments]    ${FIRST_NAME}    ${LAST_NAME}    ${EMAIL}    ${PHONE}    ${ADDRESS}    ${CITY}    ${STATE}    ${POSTAL}    ${COUNTRY}    ${UTR}
    New Page    ${PRODUCT_URL}
    Click    text="Add to Cart"
    
    # Wait for cart page or redirect
    Wait For Condition    url    contains    /cart/
    
    Go To    ${CHECKOUT_URL}
    
    # Step 1: Shipping
    Fill Text    id=id_first_name    ${FIRST_NAME}
    Fill Text    id=id_last_name     ${LAST_NAME}
    Fill Text    id=id_email         ${EMAIL}
    Fill Text    id=id_phone         ${PHONE}
    Fill Text    id=id_address       ${ADDRESS}
    Fill Text    id=id_city          ${CITY}
    Fill Text    id=id_state         ${STATE}
    Fill Text    id=id_postal_code    ${POSTAL}
    Select Options By    id=id_country    value    ${COUNTRY}
    Click    text="Next: Payment"
    
    # Step 2: Payment
    Upload File By Selector    id=id_payment_screenshot    ${CURDIR}/test_screenshot.jpg
    Fill Text    id=id_utr_number    ${UTR}
    Click    text="Next: Review"
    
    # Step 3: Review
    Click    text="Next: Confirm"
    
    # Step 4: Finalize
    Check Checkbox    id=tos-checkbox
    Click    id=submit-btn
    
    # Verify success
    Wait For Condition    url    contains    /confirmation/
    Get Text    .alert-success    contains    Order placed successfully!
