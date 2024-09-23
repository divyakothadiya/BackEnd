from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .serializers import ProductSerializer
from rest_framework.exceptions import ValidationError
from .models import Product
from django.shortcuts import get_object_or_404

class ProductCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        try:
            if serializer.is_valid():
                serializer.save()
                return Response({
                            'status': 200,
                            'message': 'Product created successfully.',
                            'data': serializer.data,
                        })
            return Response({
                        'status': 400,
                        'message': 'Something went wrong',
                        'data': serializer.errors,
                    }, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response({
                'status': 406,
                'message': 'Validation error',
                'data': e.detail,
            }, status=status.HTTP_406_NOT_ACCEPTABLE)
        except Exception as e:
            return Response({
                'status': 500,
                'message': 'An error occurred',
                'data': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ProductListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Fetch all products
            products = Product.objects.all()
            grouped_products = {}

            # Group products by category
            for product in products:
                category = product.category
                product_data = {
                    'name': product.product.get('name'),  # Assuming 'name' is within the 'product' JSON
                    'details': {key: value for key, value in product.product.items() if key != 'name'}
                }

                if category not in grouped_products:
                    grouped_products[category] = []
                
                grouped_products[category].append(product_data)

            return Response({
                'status': 200,
                'message': 'Products fetched successfully.',
                'data': grouped_products,
            })
        except Exception as e:
            return Response({
                'status': 500,
                'message': 'An error occurred',
                'data': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PDUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        product_name = request.data.get('name')  # Get the product name from request body
        category = request.data.get('category')  # Get the category from request body

        if not product_name or not category:
            return Response({
                'status': 400,
                'message': 'Product name and category are required.',
            }, status=status.HTTP_400_BAD_REQUEST)

        # Fetch product by name and category or return 404 if not found
        try:
            product = Product.objects.get(product__name=product_name, category=category)
        except Product.DoesNotExist:
            return Response({
                'status': 404,
                'message': 'Product not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        # Retrieve existing product details
        existing_product_data = product.product

        # Update or add new fields in the product data
        if 'product' in request.data:
            for key, value in request.data['product'].items():
                existing_product_data[key] = value  # This will add new fields or update existing ones

        # Prepare the updated data for saving
        updated_data = {
            'category': category,
            'product': existing_product_data,
        }

        serializer = ProductSerializer(product, data=updated_data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': 200,
                'message': 'Product updated successfully.',
                'data': serializer.data,
            })

        return Response({
            'status': 400,
            'message': 'Something went wrong',
            'data': serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        product_name = request.data.get('name')  # Get the product name from request body
        category = request.data.get('category')  # Get the category from request body

        if not product_name or not category:
            return Response({
                'status': 400,
                'message': 'Product name and category are required.',
            }, status=status.HTTP_400_BAD_REQUEST)

        # Fetch product by name and category or return 404 if not found
        try:
            product = Product.objects.get(product__name=product_name, category=category)
            product.delete()  # Delete the product
            return Response({
                'status': 204,
                'message': 'Product deleted successfully.'
            }, status=status.HTTP_204_NO_CONTENT)
        except Product.DoesNotExist:
            return Response({
                'status': 404,
                'message': 'Product not found.'
            }, status=status.HTTP_404_NOT_FOUND)
      
# class PDUpdateView(APIView):
#     permission_classes = [IsAuthenticated]

#     def put(self, request):
#         product_name = request.data.get('name')  # Get the product name from request body

#         if not product_name:
#             return Response({
#                 'status': 400,
#                 'message': 'Product name is required.',
#             }, status=status.HTTP_400_BAD_REQUEST)

#         # Fetch product by name or return 404 if not found
#         try:
#             product = Product.objects.get(product__name=product_name)
#         except Product.DoesNotExist:
#             return Response({
#                 'status': 404,
#                 'message': 'Product not found.'
#             }, status=status.HTTP_404_NOT_FOUND)

#         serializer = ProductSerializer(product, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({
#                 'status': 200,
#                 'message': 'Product updated successfully.',
#                 'data': serializer.data,
#             })

#         return Response({
#             'status': 400,
#             'message': 'Something went wrong',
#             'data': serializer.errors,
#         }, status=status.HTTP_400_BAD_REQUEST)

#     def delete(self, request):
#         product_name = request.data.get('name')  # Get the product name from request body

#         if not product_name:
#             return Response({
#                 'status': 400,
#                 'message': 'Product name is required.',
#             }, status=status.HTTP_400_BAD_REQUEST)

#         # Fetch product by name or return 404 if not found
#         try:
#             product = Product.objects.get(product__name=product_name)
#             product.delete()  # Delete the product
#             return Response({
#                 'status': 204,
#                 'message': 'Product deleted successfully.'
#             }, status=status.HTTP_204_NO_CONTENT)
#         except Product.DoesNotExist:
#             return Response({
#                 'status': 404,
#                 'message': 'Product not found.'
#             }, status=status.HTTP_404_NOT_FOUND)