from django.utils.deprecation import MiddlewareMixin

class RecentlyViewedProductsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        if 'pk' in view_kwargs:
            product_id = str(view_kwargs['pk'])

            if 'recently_viewed_products' not in request.session:
                request.session['recently_viewed_products'] = []

            recently_viewed_products = request.session['recently_viewed_products']

            if product_id in recently_viewed_products:
                recently_viewed_products.remove(product_id)

            recently_viewed_products.insert(0, product_id)

            if len(recently_viewed_products) > 5:
                recently_viewed_products = recently_viewed_products[:5]

            request.session['recently_viewed_products'] = recently_viewed_products
        return None
