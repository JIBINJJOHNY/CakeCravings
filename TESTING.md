# TESTING

## Manual Testing

Every feature that was added to the site was tested before it was integrated into the main file.

The user acceptability test listed below was used to test usability. It was distributed to new users to guarantee testing from a variety of users, on a variety of devices and browsers to ensure problems were identified and, if feasible, rectified during development.


| Page    | User Actions           | Expected Results | Y/N | Comments    |
|-------------|------------------------|------------------|------|-------------|
| Sign Up     |                        |                  |      |             |
| 1           | Click on Sign Up button | Redirection to Sign Up page | Y |          |
| 2           | Click on the Login link in the form | Redirection to Login page | Y |          |
| 3           | Enter valid email 2 times | Field will only accept email address format | Y |          |
| 4           | Enter valid password 2 times | Field will only accept password format | Y |          |
| 5           | Click on Sign Up button | asks user to confirm email page Sends address a confirmation request email | Y |          |
| 6           | Confirm email | Redirects user to blank Sign In page | Y |          |
| 7           | Sign In | Redirects user to blank In page | Y |          |
| 8           | Sign In with the same email/username and password | Takes user to schedule page with pop-up confirming successful sign in. Get started button now missing in main nav, replaced by Menu | Y |          |
| 9           | Click "Logout" button  in the center of the page| Redirects user to home page | Y |          |
| 10          | Click browser back button | You are still logged out | Y |          |
| Log In      |                        |                  |      |             |
| 1           | Click on Log In button | Redirection to Log In page | Y |          |
| 2           | Click on the Sign Up link in the form | Redirection to Sign Up page | Y |          |
| 3           | Enter valid email | Field will only accept email address format | Y |          |
| 4           | Enter valid password | Field will only accept password format | Y |          |
| 5           | Click on Log In button | Redirects user to blank In page | Y |          |
| 6           | click logout button | Redirects user to home page | Y |          |
| 7           | Click browser back button | You are still logged out | Y |          |
| 8           | Click on Log In button | Redirection to Log In page | Y |          |
| 9           | Enter valid email | Field will only accept email address format | Y |          |
| 10          | Enter valid password | Field will only accept password format | Y |          |
| 11          | Click Remember Me checkbox | Remembers user | Y |          |
| 12          | Click on Log In button | Redirects user to blank In page | Y |          |
| 13          | Click logout button | Redirects user to home page | Y |          |
| 14          | Click browser back button | You are still logged out | Y |          |
| 15          | Click on Log In button | Redirection to Log In page prefilled | Y |          |
| Navigation  |                        |                  |      |             |
| 1           | Click on the logo | Redirection to home page | Y |          |
| 2           | Click Home button | Redirection to home page | Y |          |
| 3           | Click Ourmenu button | Open dropdown-menu | Y |   Dropdown menu contains 5 buttons all products,cakes,cupcakes,cookies and seasonals        |
| 4           | Click All products button | Redirection to Products page | Y | All category products can see           |
| 5           | Click Cakes button | Redirection to Products page | Y |  Only can see cakes products list        |
| 6           | Click Cupcakes button | Redirection to Products page | Y | Only can see cupcakes products list          |
| 7           | Click Cookies button | Redirection to Products page | Y |  Only can see cookies products list          |
| 8           | Click Seasonals button | Redirection to products page | Y |  Only can see seasonal products list          |
| 9           | Click About button | Redirection to About section in home page | Y |          |
| 10          | Click Gallery button |Redirection to gallery section in home page  | Y |          |
| 11          | Click Contact button | Redirection to contact us section in home page  | Y |          |
| 12          | search input and button | Shows search products | Y |          |
| 13          | Click user icon button | Open dropdown-menu | Y | Dropdown menu contains 3 buttons profile,orders and logout        |
| 14          | Click Profile button | Redirection to Profile page | Y |          |
| 15           | Click orders button | Redirection to user orders page | Y |          |
| 16           | Click logout button | Redirection to logout page | Y |          |
| 17           | Click login button | Redirection to login page | Y |  user is not loggedin login button is showing        |
| 18           | Click wishlist button | Redirection to wishlist page | Y |          |
| 19           | Click cart button | Redirection to bag page | Y |          |
| Admin Navigation |                        |                  |      |             |
| 1           | Click Product list | Redirection to product list page | Y |          |
| Home Page  |                        |                  |      |             |
| 1           | Click Order now button | Redirection to Products page | Y |          |
| Products Page |                        |                  |      |             |
| 1 | click on breadcrumb buttons  | redirect to home page and product page | Y |          |
| 2  | Select a category | Products are displayed | Y |          |
| 3  | click on category list  | Products are displayed based on category  | Y |          |
| 4 | Click on sort by buttons | Products are correctly filtered  | Y |based  on name(ascending order and descending order) price(low to high hight zo low rating hight to low) works |
| 5  | Click on heart button | Product is added to wishlist and message will appear to notify user | Y | If user is logged out, the user will see a message to login and the click will be ignored |
| 5 | Click on the product card image | User will be redirected to the product details page | Y | |
| 6 | Click on page navigation | User will be redirected to the correct page | Y | |
| 7 | Click Back to top icon  | User will be redirected to top of page | Y | |

