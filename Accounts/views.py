from django.shortcuts import render,Franchise

# Create your views here.
# class FranchiseListView(APIView):
#     def get(self, request):
#         franchises = Franchise.objects.all()
#         serializer = FranchiseSerializer(franchises, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)