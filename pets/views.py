from django.shortcuts import render
from rest_framework.views import APIView, Response
from rest_framework.pagination import PageNumberPagination
from .models import Pet
from .serializers import PetSerializer
from groups.models import Group
from traits.models import Trait

class PetView(APIView, PageNumberPagination):
    def post(self, req):
        serializer = PetSerializer(data = req.data)
        if not serializer.is_valid():
            return Response(serializer.errors, 400)
        
        group_data = serializer.validated_data.pop("group")
        group_filter = Group.objects.filter(scientific_name__iexact = group_data["scientific_name"]).first()

        traits = serializer.validated_data.pop("traits")

        if not group_filter:
            group_filter = Group.objects.create(**group_data)
        
        create_pet = Pet.objects.create(**serializer.validated_data, group=group_filter)
        
        for item in traits:
            trait_filter = Trait.objects.filter(name__iexact = item["name"]).first()
            if not trait_filter:
                trait_filter = Trait.objects.create(**item)
            create_pet.traits.add(trait_filter)
        serializer = PetSerializer(instance = create_pet)

        return Response(serializer.data, 201)
        
    
    def get(self, req) -> Response:
        all_pets = Pet.objects.all()
        trait = req.query_params.get("trait", None)
        if trait:
            filter_trait = Trait.objects.filter(name = trait).first()
            if filter_trait:
                all_pets = Pet.objects.filter(traits=filter_trait).all()

        result_pages = self.paginate_queryset(all_pets, req)

        serializer = PetSerializer(result_pages, many=True)
        return self.get_paginated_response(serializer.data)
            
        

        

class PetDetailView(APIView, PageNumberPagination):
    def get(self, req, pet_id) -> Response:
        pet = Pet.objects.get(id = pet_id)
        serializer = PetSerializer(pet)
        return Response(serializer.data)
    def delete(self, req, pet_id):
        try:
            pet = Pet.objects.get(id = pet_id)
        except Pet.DoesNotExist:
            return Response({"detail": "Not found."}, 404)
        pet.delete()
        return Response(status=204)
    
    def patch(self, req, pet_id) -> Response:
        try:
            pet = Pet.objects.get(id = pet_id)
        except Pet.DoesNotExist:
            return Response({"detail": "Not found."}, 404)
        serializer = PetSerializer(data = req.data, partial = True)
        if not serializer.is_valid():
            return Response(serializer.errors, 400)
        group = serializer.validated_data.pop("group", None)
        traits = serializer.validated_data.pop("traits", None)

        if group:
            group_filter = Group.objects.filter(scientific_name__iexact = group["scientific_name"]).first()
            if not group_filter:
                group_filter = Group.objects.create(**group)
            pet.group = group_filter
        
        list_new_traits = []
        
        if traits:
            for item in traits:
                trait_filter = Trait.objects.filter(name__iexact = item["name"]).first()
                if not trait_filter:
                    trait_filter = Trait.objects.create(**item)
                list_new_traits.append(trait_filter)

            pet.traits.set(list_new_traits)

        for key, value in serializer.validated_data.items():
            setattr(pet, key, value)
        
        pet.save()
        serializer = PetSerializer(pet)
        return Response(serializer.data)
        
        

