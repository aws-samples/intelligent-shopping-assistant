import requests

class ToolsList:
    
    def add_cart(self,user_id:str, product_id: str, quantity: str):
        cart_info = {}
        cart_info['user_id'] = user_id
        cart_info['product_id'] = product_id
        cart_info['product_quantity'] = quantity
        print('cart_info:',cart_info)

        #####
        #use cart_info parameters to call the add cart api
        #####

        response = 'The items have been added to the shopping cart'
        return response

        
    def check_order(self,user_id:str,order_id:str):
        order_info = {}
        order_info['user_id'] = user_id
        order_info['order_id'] = order_id
        print('order_info:',order_info)

        #####
        #use order_info parameters to call the check order api
        #####

        response = 'The order infomation: The goods will arrive in 3 days'
        
        return response