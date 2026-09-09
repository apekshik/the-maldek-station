#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Variant_Horror/GondolaSystem.h"
#include "GondolaStatusSign.generated.h"
class UStaticMeshComponent;
class UMaterialInstanceDynamic;

/** Fixed platform neon. Never attach to the moving cabin. */
UCLASS()
class GAME_API AGondolaStatusSign : public AActor
{
 GENERATED_BODY()
public:
 AGondolaStatusSign();
 virtual void BeginPlay() override;
 virtual void Tick(float DeltaSeconds) override;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Status") TObjectPtr<AGondolaSystem> Gondola;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Status") bool bFarTerminal=false;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Category="Status") TObjectPtr<UStaticMeshComponent> Cabinet;
 /** BOARD, ARRIVING, DEPART, AWAY, in enum order. */
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Category="Status") TArray<TObjectPtr<UStaticMeshComponent>> Circuits;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Transient,Category="Status") EGondolaPlatformStatus CurrentStatus=EGondolaPlatformStatus::Away;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Status",meta=(ClampMin="0")) float LitStrength=7.f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Status",meta=(ClampMin="0")) float UnlitStrength=.015f;
private:
 UPROPERTY(Transient) TArray<TObjectPtr<UMaterialInstanceDynamic>> CircuitMaterials;
 void UpdateStatus();
};
