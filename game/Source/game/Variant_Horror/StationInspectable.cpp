#include "StationInspectable.h"
#include "Components/StaticMeshComponent.h"

AStationInspectable::AStationInspectable()
{
 Mesh=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
 SetRootComponent(Mesh);
 Mesh->SetMobility(EComponentMobility::Movable);
 Mesh->SetCollisionProfileName(TEXT("BlockAllDynamic"));
 DisplayName=FText::FromString(TEXT("Station object"));
}
