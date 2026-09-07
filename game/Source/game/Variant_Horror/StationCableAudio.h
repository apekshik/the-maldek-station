#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "StationCableAudio.generated.h"
class UAudioComponent;
class USoundBase;

/** Positional cable foley follows the gondola; it is silent when parked. */
UCLASS()
class GAME_API AStationCableAudio : public AActor
{
 GENERATED_BODY()
public:
 AStationCableAudio();
 virtual void BeginPlay() override;
 virtual void Tick(float DeltaSeconds) override;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Cable Audio") TObjectPtr<AActor> GondolaTarget;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Cable Audio") TObjectPtr<USoundBase> CableLoop;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Cable Audio") float CableVolume=.65f;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Category="Cable Audio") TObjectPtr<UAudioComponent> Audio;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Transient,Category="Cable Audio") float MotionAmount=0;
private:
 FVector PreviousLocation=FVector::ZeroVector;
 bool bHasLocation=false;
};
