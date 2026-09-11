#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "StationPoliceTape.generated.h"
class USplineMeshComponent;
class UStaticMesh;
class UMaterialInterface;
class USoundBase;
class USoundAttenuation;

/** Lightweight ribbon study: fixed-step flexible chains, contact and authored tear seams. */
UCLASS()
class GAME_API AStationPoliceTape : public AActor
{
 GENERATED_BODY()
public:
 AStationPoliceTape();
 virtual void OnConstruction(const FTransform& Transform) override;
 virtual void PostRegisterAllComponents() override;
 virtual void BeginPlay() override;
 virtual void Tick(float DeltaSeconds) override;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Police Tape") FVector LeftAnchor=FVector(-180,0,0);
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Police Tape") FVector RightAnchor=FVector(180,0,0);
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Police Tape") bool bCrossing=true;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Police Tape") TObjectPtr<UStaticMesh> RibbonMesh;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Police Tape") TObjectPtr<UMaterialInterface> TapeMaterial;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Police Tape",meta=(ClampMin="5",ClampMax="100")) float PushDistance=36;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Transient,Category="Police Tape") int32 BrokenStrands=0;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Transient,Category="Police Tape") float ContactSeconds=0;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Transient,Category="Police Tape") int32 RibbonContacts=0;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Police Tape|Audio") TArray<TObjectPtr<USoundBase>> TearSounds;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Police Tape|Audio") TObjectPtr<USoundAttenuation> TearAttenuation;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Police Tape|Audio",meta=(ClampMin="0",ClampMax="4")) float TearVolume=1.3f;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Transient,Category="Police Tape|Audio") int32 TearSoundEvents=0;
 UFUNCTION(BlueprintCallable,Category="Police Tape") void ResetTape();
private:
 struct FStrand { TArray<FVector> P,Old; TArray<float> Rest; FVector A,B; bool Broken=false; float ContactTime=0; };
 UPROPERTY(Transient) TArray<TObjectPtr<USplineMeshComponent>> Ribbons;
 TArray<FStrand> Strands;
 float Accumulator=0,SimulationTime=0,LastTearSoundTime=-1000;
 static constexpr int32 Segments=24;
 static constexpr int32 Seam=12;
 void Build();
 void Step(float Dt,const FVector& Player,float Radius,float HalfHeight,bool HasPlayer,bool Moving);
 void DrawRibbon();
};
