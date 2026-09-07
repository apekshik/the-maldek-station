#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "StationOpeningComponent.generated.h"
class UStationOpeningWidget;
class USoundBase;
class UAudioComponent;
class APlayerController;

UCLASS(ClassGroup=(Station),meta=(BlueprintSpawnableComponent))
class GAME_API UStationOpeningComponent : public UActorComponent
{
 GENERATED_BODY()
public:
 UStationOpeningComponent();
 virtual void TickComponent(float Dt,ELevelTick TickType,FActorComponentTickFunction* Function) override;
 virtual void EndPlay(const EEndPlayReason::Type Reason) override;
 bool AllowsFlashlightInput() const {return !bEnableOpening || (bStarted && Elapsed>=6.0f);}
 void FlashlightToggled(bool bEnabled);
 void FocusAdjusted();
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Opening") bool bEnableOpening=false;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Opening") TObjectPtr<USoundBase> OpeningAtmosphere;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Flashlight") TObjectPtr<USoundBase> SwitchOn;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Flashlight") TObjectPtr<USoundBase> SwitchOff;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Opening",meta=(ClampMin="0",ClampMax="1")) float AtmosphereVolume=.35f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Flashlight",meta=(ClampMin="0",ClampMax="1")) float SwitchVolume=.7f;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Transient,Category="Opening|Diagnostics") float Elapsed=0;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Transient,Category="Opening|Diagnostics") bool bTriedToggle=false;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Transient,Category="Opening|Diagnostics") bool bTriedFocus=false;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Transient,Category="Opening|Diagnostics") int32 SwitchCount=0;
private:
 UPROPERTY(Transient) TObjectPtr<UStationOpeningWidget> Widget;
 UPROPERTY(Transient) TObjectPtr<UAudioComponent> Atmosphere;
 UPROPERTY(Transient) TObjectPtr<APlayerController> Controller;
 bool bStarted=false,bInputHeld=false;
 void ReleaseInput();
};
