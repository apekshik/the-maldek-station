#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "StationLodgeAcoustics.generated.h"
class UAudioComponent;
class USoundBase;
UCLASS(Blueprintable)
class GAME_API AStationLodgeAcoustics: public AActor
{
 GENERATED_BODY()
public:
 AStationLodgeAcoustics();
 virtual void BeginPlay() override;
 virtual void Tick(float DeltaSeconds) override;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly) TObjectPtr<UAudioComponent> WindAudio;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) TObjectPtr<USoundBase> WindLoop;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) TArray<FVector> RoomCenters;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) TArray<FVector> RoomExtents;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) float Volume=.8f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) TObjectPtr<AActor> WeatherActor;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,meta=(ClampMin="0",ClampMax="1")) float StormIntensity=1;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Transient) float InteriorBlend=0;
 UFUNCTION(BlueprintPure) float WeightAt(FVector WorldPosition) const;
};
