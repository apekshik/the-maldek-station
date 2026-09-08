#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "GondolaMechanism.generated.h"
class AGondolaSystem;
class UMaterialInstanceDynamic;
class USoundBase;
class USoundAttenuation;
USTRUCT(BlueprintType)
struct FGondolaRotor
{
 GENERATED_BODY()
 UPROPERTY(EditAnywhere,BlueprintReadWrite) TObjectPtr<AActor> Actor;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) FVector WorldAxis=FVector(1,0,0);
 UPROPERTY(EditAnywhere,BlueprintReadWrite) float PitchRadiusCm=188.7758f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) float Ratio=1.f;
};
USTRUCT(BlueprintType)
struct FGondolaMachineSound
{
 GENERATED_BODY()
 UPROPERTY(EditAnywhere,BlueprintReadWrite) TObjectPtr<AActor> Actor;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) float RunningVolume=1.f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) float IdleVolume=0.f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) float MinimumPitch=.65f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) float MaximumPitch=1.f;
};
/** Wheel angle, rope surface transport and sound share measured cabin travel. */
UCLASS()
class GAME_API AGondolaMechanism : public AActor
{
 GENERATED_BODY()
public:
 AGondolaMechanism();
 virtual void BeginPlay() override;
 virtual void Tick(float DeltaSeconds) override;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Mechanism") TObjectPtr<AGondolaSystem> Gondola;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Mechanism") TArray<FGondolaRotor> Rotors;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Mechanism") TArray<TObjectPtr<AActor>> RopeParts;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Mechanism") TArray<FGondolaMachineSound> SoundSources;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Mechanism") TObjectPtr<USoundBase> BrakeReleaseSound;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Mechanism") TObjectPtr<USoundBase> BrakeSetSound;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Mechanism") TObjectPtr<USoundAttenuation> BrakeAttenuation;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Mechanism") FVector BrakeLocation=FVector::ZeroVector;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Transient,Category="Mechanism") float SignedSpeedCm=0;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Transient,Category="Mechanism") double RopeTravelMeters=0;
private:
 TArray<FQuat> RestRotations;
 UPROPERTY(Transient) TArray<TObjectPtr<UMaterialInstanceDynamic>> RopeMaterials;
 float PreviousDistance=0;
 float InitialDistance=0;
 float SoundMotion=0;
 bool bWasMoving=false;
 bool bHasInitialTick=false;
};
