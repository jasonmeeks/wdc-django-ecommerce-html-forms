from django.shortcuts import render, redirect
from django.http import HttpResponseNotFound

from products.models import Product, Category, ProductImage


def products(request):
    # Get all products from the DB using the Product model
    products = Product.objects.all()

    # Get up to 4 `featured=true` Products to be displayed on top
    featured_products = products.filter(featured=True)[:4]

    return render(
        request,
        'products.html',
        context={'products': products, 'featured_products': featured_products}
    )


def create_product(request):
    # Get all categories from the DB
    categories = Category.objects.all()  # <YOUR CODE HERE>
    if request.method == 'GET':
        # Render 'create_product.html' template sending categories as context
        return render(request, 'create_product.html', {'categories': categories})  # static_form is just used as an example
    elif request.method == 'POST':
        # Validate that all fields below are given in request.POST dictionary,
        # and that they don't have empty values.

        # If any errors, build an errors dictionary with the following format
        # and render 'create_product.html' sending errors and categories as context

        # errors = {'name': 'This field is required.'}
        fields = ['name', 'sku', 'price']
        errors = {}
        # <YOUR CODE HERE>
        for field in fields:
            if not request.POST.get(field):
                errors[field] = 'This field is required.'
                
        if errors:
            return render(
                request,
                'create_product.html',
                context={'categories': categories, 'errors':errors}
            )

        # If no errors so far, validate each field one by one and use the same
        # errors dictionary created above in case that any validation fails

        # name validation: can't be longer that 100 characters
        name = request.POST.get('name')
        if len(name) > 100:
            errors['name'] = "Name can't be longer than 100 characters."

        # SKU validation: it must contain 8 alphanumeric characters
        # <YOUR CODE HERE>
        sku = request.POST.get('sku')
        if len(sku) != 8:
            errors['sku'] = "Sku must contain 8 alphanumeric characters."

        # Price validation: positive float lower than 10000.00
        # <YOUR CODE HERE>
        price = request.POST.get('price')
        if price >= 10000 or price < 0:
            errors['price'] = "Price must be positive and less than 10000.00."

        # if any errors so far, render 'create_product.html' sending errors and
        # categories as context
        # <YOUR CODE HERE>
        if errors:
            return render(
                request,
                'create_product.html',
                context={'categories': categories, 'errors':errors}
            )
        
        # If execution reaches this point, there aren't any errors.
        # Get category from DB based on category name given in payload.
        # Create product with data given in payload and proper category
        category = Category.objects.get(name=request.POST.get('category'))
        product = Product.objects.create(
            name=request.POST.get('name'),
            sku=request.POST.get('sku'),
            price=float(request.POST.get('price')),
            category=request.POST.get('category'),
            description=request.POST.get('description', '')
        )

        # Up to three images URLs can come in payload with keys 'image-1', 'image-2', etc.
        # For each one, create a ProductImage object with proper URL and product
        # <YOUR CODE HERE>
        images = []
        for i in range(1, 4):
            image = request.POST.get('image_{}'.format(i))
            if image:
                images.append(image)

        for image in images:
            ProductImage.objects.create(
                product=product,
                url=image
        )    

        # Redirect to 'products' view
        return redirect('products')


def edit_product(request, product_id):
    # Get product with given product_id
    product = Product.objects.get(id=product_id)

    # Get all categories from the DB
    categories = Category.objects.all()
    if request.method == 'GET':
        # Render 'edit_product.html' template sending product, categories and
        # a 'images' list containing all product images URLs.
        return render(request, 'edit_product.html', {
            'product': product, 
            'categories': categories, 
            'images': [image.url for image in product.productimage_set.all()]})

    elif request.method == 'POST':
        # Validate following fields that come in request.POST in the very same
        # way that you've done it in create_product view
        fields = ['name', 'sku', 'price']
        errors = {}
        # <YOUR CODE HERE>

        for field in fields:
            if not request.POST.get(field):
                errors[field] = 'This field is required.'
                
        if errors:
            return render(
                request,
                'create_product.html',
                context={'categories': categories, 'errors':errors}
            )
            
        # name validation: can't be longer that 100 characters
        name = request.POST.get('name')
        if len(name) > 100:
            errors['name'] = "Name can't be longer than 100 characters."

        # SKU validation: it must contain 8 alphanumeric characters
        # <YOUR CODE HERE>
        sku = request.POST.get('sku')
        if len(sku) != 8:
            errors['sku'] = "Sku must contain 8 alphanumeric characters."

        # Price validation: positive float lower than 10000.00
        # <YOUR CODE HERE>
        price = request.POST.get('price')
        if price >= 10000 or price < 0:
            errors['price'] = "Price must be positive and less than 10000.00."

        # if any errors so far, render 'create_product.html' sending errors and
        # categories as context
        # <YOUR CODE HERE>
        if errors:
            return render(
                request,
                'create_product.html',
                context={'categories': categories, 'errors':errors}
            )

        # If execution reaches this point, there aren't any errors.
        # Update product name, sku, price and description from the data that
        # come in request.POST dictionary.
        # Consider that ALL data is given as string, so you might format it
        # properly in some cases.
        category = Category.objects.get(name=request.POST.get('category'))
        product = Product.objects.create(
            name=request.POST.get('name'),
            sku=request.POST.get('sku'),
            price=float(request.POST.get('price')),
            category=request.POST.get('category'),
            description=request.POST.get('description', '')
        )

        # Get proper category from the DB based on the category name given in
        # payload. Update product category.
        category = Product.objects.get(category=request.POST.get('category'))
        product.category = category
        product.save()

        # For updating the product images URLs, there are a couple of things that
        # you must consider:
        # 1) Create a ProductImage object for each URL that came in payload and
        #    is not already created for this product.
        # 2) Delete all ProductImage objects for URLs that are created but didn't
        #    come in payload
        # 3) Keep all ProductImage objects that are created and also came in payload
        # <YOUR CODE HERE>
        
        # get new images
        posted_images = []
        for i in range(1, 4):
            image = request.POST.get('image_{}'.format(i))
            if image:
                posted_images.append(image)
        
        # get old images
        old_images = [image.url for image in product.productimage_set.all()]

        # find old images not included in new images and delete them
        images_to_delete = []
        for image in old_images:
            if image not in posted_images:
                images_to_delete.append(image)
        ProductImage.objects.filter(url__in=images_to_delete).delete()

        # create new images
        for image in posted_images:
            ProductImage.objects.create(
                product=product,
                url=image
        )    

        # Redirect to 'products' view
        return redirect('products')


def delete_product(request, product_id):
    # Get product with given product_id
    product = Product.objects.get(id=product_id)
    if request.method == 'GET':
        # render 'delete_product.html' sending product as context
        return render(request, 'delete_product.html', {'product': product})
    elif request.method == "POST":
        # Delete product and redirect to 'products' view
        product.delete()
        return redirect('products')


def toggle_featured(request, product_id):
    # Get product with given product_id
    product = Product.objects.get(id=product_id)

    # Toggle product featured flag
    product.featured = not product.featured
    product.save()

    # Redirect to 'products' view
    return redirect('products')
